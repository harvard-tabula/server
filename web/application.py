from . import app, db
from .models import User
import os


@app.route("/")
def index():
    db.create_all()
    admin = User('admin@tabula.life')
    db.session.add(admin)
    return "The stasrt of something beautiful!"


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
