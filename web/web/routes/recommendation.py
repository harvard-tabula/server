from web.models import db, Course
from web.routes import api
from flask_restful import Resource, reqparse
from flask_login import login_required


class Recommendation(Resource):  # TODO Plug in an actual recommendation algorithm
    decorators = [login_required]

    def get(self, course_id):
        course = db.session.query(Course).filter(Course.id == course_id).one_or_none()

        if not course:
            return {'state': 404, 'message': 'No course with that ID'}

        res = {
            'course': {
                'id': course.id,
                'catalog_number': course.name_short,
                'title': course.name_long,
                'description': course.description,
            },
            'grade': 'A-',
            'hours': 10,
            'associated_tags': [
                {
                    "category": "academic",
                    "id": 50,
                    "name": "Systems",
                }, {
                    "category": "academic",
                    "id": 50,
                    "name": "Networks",
                }, {
                    "category": "user_history",
                    "id": 50,
                    "name": "Happy",
                }
            ],
        }

        result = {
            'state': 200,
            'message': 'Recommendation successfully generated.',
            'data': res
        }

        return result

api.add_resource(Recommendation, '/recommendation/<int:course_id>')
