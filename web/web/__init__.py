from flask import Flask
from web import config
from web.models import db
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)

CORS(app, origins='http://localhost:3000', supports_credentials=True, expose_headers=[
        'Access-Control-Allow-Origin',
        'Access-Control-Allow-Credentials',
        'Access-Control-Allow-Headers',
        'Access-Control-Allow-Methods'
    ])

db.init_app(app)

from web.routes import util, auth, course, user, recommendation
