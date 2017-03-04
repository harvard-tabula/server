from . import app, models, db
import os
from flask import redirect, session, request
from flask_restful import Resource, Api
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
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
def load_user(user_id):
    return User.query.get(int(user_id))


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


class Login(Resource):

    def get(self):
        if current_user.is_authenticated:
            return redirect('/profile')
        google = get_google_auth()
        auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline', hd='college.harvard.edu')
        session['oauth_state'] = state
        return redirect(auth_url)


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
                hd = user_data.get('hd')
                if not hd or hd != 'college.harvard.edu':
                    return {'state': 403, 'message': 'Only Harvard College students have access to Tabula.'}

                email = user_data['email']
                user = User.query.filter_by(email=email).first()
                if user is None:
                    name = user_data['name']
                    avatar = user_data['picture']
                    tokens = json.dumps(token)
                    user = User(email, name, avatar, tokens)
                user.active = True

                db.session.add(user)
                db.session.commit()
                login_user(user, remember=False)
                return redirect('/profile')
            return {'state': 'could not fetch information'}


class Logout(Resource):

    decorators = [login_required]

    def get(self):
        if app.config['DEBUG']:
            logout_user()
            return redirect('https://www.tabula.life')
        return {'state': 400, 'message': 'Logout requests must be made via post in production.'}

    def post(self):
        logout_user()
        return redirect('https://www.tabula.life')


class Profile(Resource):
    decorators = [login_required]

    def get(self):
        return {'state': 200, 'data': {'UserProfile': True, 'UserHistory': True}}


api.add_resource(Login, '/login', endpoint='login')
api.add_resource(OAuth2Callback, '/oauth2callback', endpoint='oauth2callback')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Profile, '/profile', endpoint='profile')

app.secret_key = os.environ['SECRET_KEY']

if __name__ == '__main__':
    app.run()
