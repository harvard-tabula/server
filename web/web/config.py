import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
        os.environ['DB_USER'],
        os.environ['DB_PASS'],
        os.environ['DB_HOST'],
        os.environ['DB_PORT'],
        os.environ['DB_NAME']
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SALT = os.environ['SALT']


class Auth:
    CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
    CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
    REDIRECT_URI = os.environ['API_BASE'] + '/oauth2callback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = {
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    }


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
