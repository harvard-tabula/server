from . import app, db
from .models import User, UserProfile, Course, Concentration, Tag, UserHistory, Semester, Gender, Ethnicity, Grade, Term
from flask import redirect, session, request, make_response
from flask_restful import Resource, Api
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from .config import Auth
import json
import hashlib
from collections import Counter
from flask_restful import reqparse

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
    return user_hash.hex()


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
            user = current_user
            user.authenticated = False
            logout_user()
            resp = make_response(redirect('/'))
            resp.set_cookie('session', value='', expires=0)
            # return resp
            return {}
        return {'state': 400, 'message': 'Logout requests must be made via post in production.'}

    def post(self):
        user = current_user
        user.authenticated = False
        db.session.add(user)
        db.session.commit()
        logout_user()
        resp = make_response(redirect('/'))
        resp.set_cookie('session', '', expires=0)
        return resp


api.add_resource(Login, '/login')
api.add_resource(OAuth2Callback, '/oauth2callback')
api.add_resource(Logout, '/logout')


###############################
# STATEFUL RESOURCES
###############################
class Profile(Resource):
    decorators = [login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("name", location="json", type=str)
        self.parser.add_argument("gender", location="json", type=str)
        self.parser.add_argument("tag_ids", location="json", type=list)
        self.parser.add_argument("concentration", location="json", type=str)
        self.parser.add_argument("ethnicity", location="json", type=str)
        self.parser.add_argument("years_coding", location="json", type=float)
        self.parser.add_argument("year", location="json", type=int)

        self.user_hash = session['user_hash']

    def get(self):

        user_profile = db.session.query(UserProfile).filter(UserProfile.user_hash == self.user_hash).first()
        if not user_profile:
            return {
                'state': 404,
                'message': 'Could not find user\'s profile.'
            }

        tags = [
            {
                'id': tag.id,
                'name': tag.name,
                'category': tag.category
            }
            for tag in user_profile.tags
        ]

        result = {
            'state': 200,
            'message': 'User Profile retrieved successfully.',
            'data': {
                'name': current_user.name,
                'email': current_user.email,
                'avatar': current_user.avatar,
                'tags': tags,
                'concentration': user_profile.concentration.name if user_profile.concentration else None,
                'gender': user_profile.gender,
                'ethnicity': user_profile.ethnicity,
                'years_coding': user_profile.years_coding,
                'year': user_profile.year
            }
        }

        return result

    def put(self):

        user_profile = db.session.query(UserProfile).filter(UserProfile.user_hash == self.user_hash).one_or_none()
        if not user_profile:
            return {
                'state': 404,
                'message': 'Could not find user\'s profile.'
            }

        args = self.parser.parse_args()

        # Handle concentration id <> name conversion
        user_profile.concentration_id = db.session.query(Concentration.id).filter(
            Concentration.name == args['concentration']
        ).one_or_none()

        # Handle tags
        user_profile.tags.clear()
        new_tags = []
        for tag_id in args['tag_ids']:
            new_tags.append(
                db.session.query(Tag).filter(Tag.id == tag_id).one_or_none()
            )

        user_profile.tags = [tag_id for tag_id in new_tags if tag_id is not None]

        # Handle general profile data
        if args.get('gender'):
            if args['gender'] in Gender:
                user_profile.gender = args['gender']
            else:
                return {'state': 400, 'message': 'Not a valid gender'}

        if args.get('ethnicity'):
            if args['ethnicity'] in Ethnicity:
                user_profile.ethnicity = args['ethnicity']
            else:
                return {'state': 400, 'message': 'Not a valid ethnicity'}

        user_profile.years_coding = args['years_coding']
        user_profile.year = args['year']
        user_profile.name = args['name']

        db.session.commit()
        return {'state': 201, 'message': 'Successfully updated profile.'}


class History(Resource):
    decorators = [login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("semester", location="json", type=str)
        self.parser.add_argument("grade", location="json", type=str)
        self.parser.add_argument("id", location="json", type=int)
        self.parser.add_argument("hours", location="json", type=int)
        self.parser.add_argument("course_tag_ids", location="json", type=list)


        self.user_hash = session['user_hash']

    def get(self):

        result = []
        user_histories = db.session.query(UserHistory).filter(UserHistory.user_hash == self.user_hash).all()
        for user_history in user_histories:

            course_tags = [
                {
                    'id': course_tag.id,
                    'name': course_tag.name,
                    'category': course_tag.category
                }
                for course_tag in user_history.course_tags
            ]

            result.append({
                'id': user_history.id,
                'semester': "{} {}".format(user_history.semester.term, user_history.semester.year),
                'grade': user_history.grade,
                'course_tags': course_tags,
                'hours': user_history.hours,
                'course': {
                    'id': user_history.course.id,
                    'harvard_id': user_history.course.harvard_id,
                    'name_short': user_history.course.name_short,
                    'name_long': user_history.course.name_long,
                    'description': user_history.course.description,
                    'concentration': user_history.course.concentration.name
                }
            })

        return {'state': 200, 'data': result}

    def put(self):

        args = self.parser.parse_args()

        term, year = args['semester'].split(' ')
        if term not in Term:
            return {'state': 404, 'message': 'Invalid term'}

        semester_id = db.session.query(Semester.id).filter(Semester.term == term, Semester.year == year).one_or_none()
        if not semester_id:
            return {'state': 404, 'message': 'Could not find semester ID.'}

        user_history = db.session.query(UserHistory).filter(
            UserHistory.user_hash == self.user_hash,
            UserHistory.course_id == args['id'],
            UserHistory.semester_id == semester_id
        ).one_or_none()

        grade = None
        if args.get('grade'):
            if args['grade'] in Grade:
                grade = args['grade']
            else:
                return {'state': 400, 'message': 'Not a valid grade'}

        if not user_history:  # Create
            user_history = UserHistory(self.user_hash, args['id'], semester_id, grade)
            db.session.add(user_history)

        else:  # Update
            user_history.semester_id = semester_id
            user_history.grade = grade
            user_history.course_id = args['id']

        # Handle tags
        if args.get('course_tag_ids'):
            new_course_tags = []
            for course_tag_id in args['course_tag_ids']:
                new_course_tags.append(
                    db.session.query(Tag).filter(Tag.id == course_tag_id).one_or_none()
                )
            user_history.course_tags.clear()
            user_history.course_tags = [course_tag_id for course_tag_id in new_course_tags if course_tag_id is not None]

        user_history.hours = args.get('hours')

        db.session.commit()

        return {'state': 201, 'message': 'Successfully updated user_history.'}

    def delete(self):

        args = self.parser.parse_args()

        term, year = args['semester'].split(' ')
        if term not in Term:
            return {'state': 404, 'message': 'Invalid term'}
        semester_id = db.session.query(Semester.id).filter(Semester.term == term, Semester.year == year).one_or_none()
        if not semester_id:
            return {'state': 404, 'message': 'Could not find semester ID.'}

        user_history = db.session.query(UserHistory).filter(
            UserHistory.user_hash == self.user_hash,
            UserHistory.course_id == args['id'],
            UserHistory.semester_id == semester_id
        ).one_or_none()

        if not user_history:
            return {'state': 404, 'message': 'No user_history to delete'}
        else:
            db.session.delete(user_history)
            db.session.commit()
            return {'state': 204, 'message': 'Deleted user_history for given course ID'}


api.add_resource(Profile, '/profile')
api.add_resource(History, '/history')


###############################
# STATELESS RESOURCES
###############################
class Test(Resource):

    def get(self):
        return {'state': 200, 'message': 'Ping!'}


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
    decorators = [login_required]

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
    decorators = [login_required]

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


class Tags(Resource):
    decorators = [login_required]

    def get(self):
        tags = db.session.query(Tag).all()
        result = [
            {
                "category": tag.category,
                "id": tag.id,
                "name": tag.name
            }
            for tag in tags
        ]

        return {'state': 200, 'message': 'Tags retrieved successfully', 'data': result}

    def post(self):
        pass


class Concentrations(Resource):
    decorators = [login_required]

    def get(self):
        concentrations = db.session.query(Concentration).all()
        result = [
            {
                "id": concentration.id,
                "name": concentration.name
            }
            for concentration in concentrations
        ]

        return {'state': 200, 'message': 'Tags retrieved successfully', 'data': result}

    def post(self):
        pass


class Semesters(Resource):
    decorators = [login_required]

    def get(self):
        semesters = db.session.query(Semester).all()
        result = [
            {
                "id": semester.id,
                "semester": '{} {}'.format(semester.term, semester.year)
            }
            for semester in semesters
        ]

        return {'state': 200, 'message': 'Tags retrieved successfully', 'data': result}

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


api.add_resource(Test, '/')
api.add_resource(AllCourses, '/allcourses', '/allcourses/page/<int:page>')
api.add_resource(Courses, '/courses/<int:course_id>')
api.add_resource(CourseSearch, '/coursesearch/<string:query>')
api.add_resource(Tags, '/tags')
api.add_resource(Concentrations, '/concentrations')
api.add_resource(Semesters, '/semesters')


app.secret_key = app.config['SECRET_KEY']

if __name__ == '__main__':
    app.run()
