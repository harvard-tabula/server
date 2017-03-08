from . import app, db
from .models import User, UserProfile, Course
from flask import redirect, session, request
from flask_restful import Resource, Api
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from .config import Auth
import json
import hashlib
from collections import Counter

api = Api(app)

###############################
# AUTHENTICATION
###############################

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


def get_user_hash(app_unique_id):
    user_hash = hashlib.pbkdf2_hmac('sha256',
                                    bytes(app_unique_id, encoding='utf-8'),
                                    bytes(app.config['SALT'], encoding='utf-8'),
                                    100000)
    return str(user_hash)


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

        if current_user is not None and current_user.is_authenticated:  # TODO Hash stored in session?
            return redirect('profile')

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
                if not hd or hd != 'college.harvard.edu':
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

                return redirect('profile')

            return {'state': 500, 'message': 'Unable to authenticate token.'}


class Logout(Resource):

    decorators = [login_required]

    def get(self):
        if app.config['DEBUG']:
            logout_user()
            return {'state': 200, 'message': 'Successfully logged out.'}
        return {'state': 400, 'message': 'Logout requests must be made via post in production.'}

    def post(self):
        logout_user()
        return redirect('https://www.tabula.life')


api.add_resource(Login, '/login')
api.add_resource(OAuth2Callback, '/oauth2callback')
api.add_resource(Logout, '/logout')


###############################
# STATEFUL RESOURCES
###############################
class Profile(Resource):
    decorators = [login_required]

    def get(self):

        user_hash = session['user_hash']
        user_profile = db.session.query(UserProfile).filter(UserProfile.user_hash == user_hash).first()
        if not user_profile:
            return {
                'state': 404,
                'message': 'Could not find user\'s profile.'
            }

        result = {
            'state': 200,
            'message': 'User Profile retrieved successfully.',
            'data': {
                'name': current_user.name,
                'email': current_user.email,
                'avatar': current_user.avatar,
                'tags': user_profile.tags,
                'concentration': user_profile.concentration,
                'gender': user_profile.gender,
                'ethnicity': user_profile.ethnicity,
                'years_coding': user_profile.years_coding,
                'year': user_profile.year
            }
        }

        return result

    def post(self, data):
        # TODO
        return {'state': 201, 'message': 'Successfully updated profile.', 'data': data}


class History(Resource):
    decorators = [login_required]

    def get(self):
        return {'state': 200, 'data': {}}

    def post(self, data):
        return {'state': 201, 'data': {'id': data}, 'message': 'Successfully updated profile.'}


api.add_resource(Profile, '/profile')
api.add_resource(History, '/history')


###############################
# STATELESS RESOURCES
###############################
class AllCourses(Resource):

    decorators = [login_required]

    def __init__(self):
        self.page_size = 20

    def get(self, page=1):
        count = db.session.query(Course).count()
        lix = (page - 1) * self.page_size + 1
        if lix > count:
            return {'state': 500, 'message': 'Out of courses'}
        num_courses = min(self.page_size, count - lix)
        rix = lix + num_courses - 1
        courses = db.session.query(Course).filter(lix <= Course.id, Course.id <= rix)
        result = {
            'state': 200,
            'message': 'Courses successfully retrieved.',
            'data': []
        }
        for course in courses:
            result['data'].append({
                                    'id': course.id,
                                    'catalogue_number': course.name_short,
                                    'title': course.name_long,
                                    'description': course.description
                                   })

        return result


class Courses(Resource):

    def get(self, course_id):

        course = db.session.query(Course).filter(Course.id == course_id)

        result = {
            'state': 200,
            'message': 'Course successfully retrieved.',
            'data': []
        }

        result['data'].append({
                                'id': course[0].id,
                                'catalogue_number': course[0].name_short,
                                'title': course[0].name_long,
                                'description': course[0].description
                               })

        return result


class CourseSearch(Resource):

    def get(self, query):

        tokens = query.split(' ')
        courses = Counter()
        for token in tokens:
            res = db.session.query(Course).filter(
                    Course.name_long.like('%{}%'.format(token)) |
                    Course.name_short.like('%{}%'.format(token)) |
                    Course.description.like('%{}%'.format(token))
                    ).limit(20)
            courses.update([course for course in res])

        result = {
            'state': 200,
            'message': 'Courses successfully retrieved.',
            'data': [
                {
                    'id': course.id,
                    'catalogue_number': course.name_short,
                    'title': course.name_long,
                    'description': course.description
                }
                for course, rank in courses.most_common(10)
            ]
        }

        return result


api.add_resource(AllCourses, '/allcourses', '/allcourses/page/<int:page>')
api.add_resource(Courses, '/courses/<int:course_id>')
api.add_resource(CourseSearch, '/coursesearch/<string:query>')


class Tags(Resource):

    def get(self, query):
        pass

    @login_required
    def post(self):
        pass


class Concentrations(Resource):

    def get(self, query):
        pass

    @login_required
    def post(self):
        pass


class Semesters(Resource):

    def get(self, query):
        pass

    @login_required
    def post(self):
        pass


class UserHistories(Resource):
    decorators = [login_required]

    def get(self, query):
        pass

    def post(self):
        pass


class UserProfiles(Resource):
    decorators = [login_required]

    def get(self, query):
        pass

    def post(self):
        pass




app.secret_key = app.config['SECRET_KEY']

if __name__ == '__main__':
    app.run()
