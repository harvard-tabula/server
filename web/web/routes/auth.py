from web import app
from web.models import db, User, UserProfile
from web.routes import api
from flask import session, request, redirect
from flask_restful import Resource, reqparse
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from web.config import Auth
import json
import hashlib


login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    # if state:  # TODO Figure out how to use state correctly.
    #     return OAuth2Session(
    #         Auth.CLIENT_ID,
    #         state=state,
    #         redirect_uri=Auth.REDIRECT_URI)
    return OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)


def get_user_hash(app_unique_id):
    user_hash = hashlib.pbkdf2_hmac('sha256',
                                    bytes(app_unique_id, encoding='utf-8'),
                                    bytes(app.config['SALT'], encoding='utf-8'),
                                    100000)
    return user_hash.hex()


class Login(Resource):

    def get(self):
        if current_user.is_authenticated:
            return {
                'state': 200,
                'message': 'User is authenticated. Please continue.',
            }
        google = get_google_auth()
        auth_url, state = google.authorization_url(
            Auth.AUTH_URI, access_type='offline', hd='college.harvard.edu')
        session['oauth_state'] = state
        return {
            'state': 302,
            'message': 'The browser must be manually redirected',
            'redirect': auth_url
        }


class OAuth2Callback(Resource):  # TODO Figure out where the user wanted to go for the redirect.

    """
    Note: This endpoint is only ever hit by the browser. Google's auth server redirects the *browser*, NOT the frontend.
    """

    def get(self):

        if current_user is not None and current_user.is_authenticated:
            return redirect("http://localhost:3000/user")

        if 'error' in request.args:
            if request.args.get('error') == 'access_denied':
                return {'state': 401, 'message': 'User denied access to Tabula.'}
            return {'state': 400}

        if 'code' not in request.args and 'state' not in request.args:
            return {'state': 400}

        else:
            google = get_google_auth(state=session['oauth_state'])
            try:
                token = google.fetch_token(
                    Auth.TOKEN_URI,
                    client_secret=Auth.CLIENT_SECRET,
                    authorization_response=request.url)
            except HTTPError:
                return {'state': '500', 'message': 'Unable to authenticate token.'}
            google = get_google_auth(token=token)
            resp = google.get(Auth.USER_INFO)

            if resp.status_code == 200:
                user_data = resp.json()
                hd = user_data.get('hd')
                if not hd or hd != 'college.harvard.edu':  # TODO: Frontend should probably have a generic error model.
                    return {'state': 401, 'message': 'Only Harvard College students have access to Tabula.'}

                email = user_data['email']
                user = User.query.filter_by(email=email).first()
                user_hash = get_user_hash(user_data['id'])
                session['user_hash'] = user_hash

                if user is None:  # New user

                    name = user_data['name']
                    avatar = user_data['picture']
                    user = User(email, name, avatar)

                    user_profile = UserProfile(session['user_hash'])
                    db.session.add(user_profile)
                    db.session.commit()

                    user.active = True

                # Update or instantiate user's oauth tokens
                tokens = json.dumps(token)
                user.tokens = tokens

                db.session.add(user)
                db.session.commit()

                login_user(user, remember=False)

                return redirect("http://localhost:3000/user")

            return {'state': 500, 'message': 'Unable to authenticate token.'}


class Logout(Resource):

    decorators = [login_required]

    def post(self):
        user = current_user
        user.authenticated = False
        db.session.commit()
        logout_user()
        return {}


api.add_resource(Login, '/login')
api.add_resource(OAuth2Callback, '/oauth2callback')
api.add_resource(Logout, '/logout')
