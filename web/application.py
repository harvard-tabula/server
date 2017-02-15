import os
from flask import Flask, session, request


# configure application
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route("/")
def index():
    return "The start of something beautiful"


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


# app.secret_key = app.config['SECRET_KEY']

if __name__ == '__main__':
    app.run()