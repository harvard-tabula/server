from flask_restful import Resource
from web.routes import api
from web.models import Ethnicity, Gender, Grade, Term, Categories
from flask_login import login_required


class Ping(Resource):

    def get(self):
        return {'state': 200, 'message': 'Ping!', 'data': []}


class UI(Resource):
    decorators = [login_required]

    def get(self):

        return {
            'state': 200,
            'message': 'Fields retrieved successfully',
            'data': {
                'ethnicities': list(Ethnicity),
                'genders': list(Gender),
                'grades': list(Grade),
                'terms': list(Term),
                'tags_categories': Categories
            }
        }


api.add_resource(Ping, '/')
api.add_resource(UI, '/ui')
