from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import config
from flask_cors import CORS

app = Flask(__name__)
CORS(app, allow_headers=['Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials', 'Access-Control-Allow-Headers', 'Access-Control-Allow-Methods'], origins='http://localhost:3000', supports_credentials=True)
app.config.from_object(config.DevelopmentConfig)
db = SQLAlchemy(app)
