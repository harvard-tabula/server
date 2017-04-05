from flask_restful import Resource
from web.routes import api


class Ping(Resource):

    def get(self):
        return {'state': 200, 'message': 'Ping!', 'data': []}

api.add_resource(Ping, '/')
