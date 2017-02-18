from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)

    def __init__(self, email):
        self.email = email
        # TODO Potentially also instantiate separate table

    def __repr__(self):
        return '<User %r>' % self.email


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hash = db.Column(db.String(255), unique=True)
    concentration_id = db.Column(db.Integer, db.ForeignKey('concentration.id'))
    gender = db.Column(db.String(10))
    ethnicity = db.Column(db.String(20))
    years_coding = db.Column(db.Float)
    year = db.Column(db.String(4))


class Concentration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    user_profiles = db.relationship('UserProfile', backref='concentration')


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)           # e.g. 1452974
    name_short = db.Column(db.String(20))  # e.g. CS164
    name_long = db.Column(db.String(255))  # e.g. Software Engineering
    description = db.Column(db.Text)
    prerequisites = db.relationship('Course', backref='course')  # TODO Self reference?
    course_histories = db.relationship('CourseHistory',  backref='course')


class CourseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hash = db.Column(db.String(255), unique=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    grade = db.Column(db.String(3))
    hours = db.Column(db.Float)
    difficulty = db.Column(db.Int)
    learning = db.Column(db.Int)
    enjoyment = db.Column(db.Int)


class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    course_histories = db.relationship('CourseHistory', backref='semester')


class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pass # TODO


class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pass # TODO

