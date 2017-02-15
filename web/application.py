from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from . import config
import os


app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = 'http://0.0.0.0:5432'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email

# db.create_all()


@app.route("/")
def index():
    admin = User('admin@tabula.life')

    # db.session.add(admin)
    return "The start of something beautiful!"


@app.route("/login", methods=['POST'])
def login():
    """
    session['username'] = request.form.get('username', '')
    """
    pass


@app.route("/logout")
def logout():
    """
    session.pop('username', None)
    """
    pass


@app.route('/profile/<int:user_id>')
def show_user_profile(user_id):
    return 'Hello user {}'.format(user_id)


app.secret_key = os.environ['SECRET_KEY']

if __name__ == '__main__':
    app.run()