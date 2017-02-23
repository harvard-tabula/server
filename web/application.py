from . import app, models, db
import os
from flask import url_for, redirect, session, request
from flask_restful import Resource, Api
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from .config import Auth
import json

User = models.User
api = Api(app)


login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')


class Login(Resource):
    def get(self):
        if current_user.is_authenticated:
            return {'logged': 'in'}
        google = get_google_auth()
        auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline')
        session['oauth_state'] = state
        return redirect(auth_url, code=302)

api.add_resource(Login, '/login')


class OAuth2Callback(Resource):

    def get(self):
        # Redirect user to home page if already logged in.
        if current_user is not None and current_user.is_authenticated:
            return {'state': 'already logged in'}
        if 'error' in request.args:
            if request.args.get('error') == 'access_denied':
                return {'state': 'user denied access'}
            return {'state': 'error'}
        if 'code' not in request.args and 'state' not in request.args:
            return {'state': 'must login'}
        else:
            # Execution reaches here when user has
            # successfully authenticated our app.
            google = get_google_auth(state=session['oauth_state'])
            try:
                token = google.fetch_token(
                    Auth.TOKEN_URI,
                    client_secret=Auth.CLIENT_SECRET,
                    authorization_response=request.url)
            except HTTPError:
                return {'state': 'HTTPError'}
            google = get_google_auth(token=token)
            resp = google.get(Auth.USER_INFO)
            if resp.status_code == 200:
                user_data = resp.json()
                email = user_data['email']
                user = User.query.filter_by(email=email).first()
                if user is None:
                    name = user['name']
                    avatar = user['picture']
                    tokens = json.dumps(token)
                    user = User(email, name, avatar, tokens)

                db.session.add(user)
                db.session.commit()
                login_user(user)
                return {'state': 'success', 'data': user_data}
            return {'state': 'could not fetch information'}


api.add_resource(OAuth2Callback, '/oauth2callback')


@app.route("/logout")
def logout():
    """
    session.pop('username', None)
    """
    pass


@login_required
@app.route('/profile/<int:user_id>')
def show_user_profile(user_id):
    return 'Hello user {}'.format(user_id)

app.secret_key = os.environ['SECRET_KEY']

if __name__ == '__main__':
    app.run()
