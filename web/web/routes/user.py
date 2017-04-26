from web.models import db, User, UserProfile, Semester, UserHistory, Tag, Term, Grade, Ethnicity, Gender
from web.routes import api
from flask import session
from flask_restful import Resource, reqparse
from flask_login import LoginManager, login_required, current_user


#
#  These are all stateful. The response will depend on the current session.
#
class Profile(Resource):
    decorators = [login_required]

    def __init__(self):

        # TODO Is there a way to pull this information from somewhere else (e.g. model) to increase modularity?
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("name", location="json", type=str)
        self.parser.add_argument("gender", location="json", type=str)
        self.parser.add_argument("tag_ids", location="json", type=list)
        self.parser.add_argument("concentration_id", location="json", type=int)
        self.parser.add_argument("ethnicity", location="json", type=str)
        self.parser.add_argument("years_coding", location="json", type=float)
        self.parser.add_argument("year", location="json", type=int)

        self.user_hash = session['user_hash']

    def get(self):

        user_profile = db.session.query(UserProfile).filter(UserProfile.user_hash == self.user_hash).one_or_none()
        if not user_profile:  # TODO Add logging here, since this should really never happen.
            return {
                'state': 500,
                'message': 'Could not find user\'s profile.'
            }

        tags = [  # TODO Currently leaving out tag.description, since we've not populated that in the DB
            {
                'id': tag.id,
                'name': tag.name,
                'category': tag.category,
            }
            for tag in user_profile.tags
        ]

        concentration = None
        if user_profile.concentration:
            concentration = {
                'id': user_profile.concentration.id,
                'name': user_profile.concentration.name,
            }

        result = {
            'state': 200,
            'message': 'User Profile retrieved successfully.',
            'data': {
                'name': current_user.name,
                'email': current_user.email,
                'avatar': current_user.avatar,
                'tags': tags,
                'concentration': concentration,
                'gender': user_profile.gender,
                'ethnicity': user_profile.ethnicity,
                'years_coding': user_profile.years_coding,
                'year': user_profile.year
            }
        }

        return result

    def put(self):

        user_profile = db.session.query(UserProfile).filter(UserProfile.user_hash == self.user_hash).one_or_none()
        if not user_profile:  # TODO Add logging here, since this should really never happen.
            return {
                'state': 500,
                'message': 'Could not find user\'s profile.'
            }

        args = self.parser.parse_args()

        # TODO Wrap the commit in a try - except block to handle errors with out of bound IDs.
        user_profile.concentration_id = args['concentration_id']

        if args['tag_ids']:
            tag_ids = args['tag_ids']
            if len(tag_ids) > 0:
                user_profile.tags = db.session.query(Tag).filter(Tag.id.in_(args['tag_ids'])).all()

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
                    'department': user_history.course.department.name,
                    'prerequisites': user_history.course.prerequisites
                }
            })

        def key_func(course):
            term, year = course['semester'].split(' ')[0], course['semester'].split(' ')[1]
            return year, Term.index(term)

        return {'state': 200, 'data': sorted(result, key=key_func)}

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
