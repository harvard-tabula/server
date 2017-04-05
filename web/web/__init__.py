from flask import Flask
from web import config
from web.models import db

app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
db.init_app(app)

from web.routes import util, auth, course, user
