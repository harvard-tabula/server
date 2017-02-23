from . import db
import datetime


interests = db.Table('interests',
     db.Column('user_profile_id', db.Integer, db.ForeignKey('user_profile.id')),  # NB: Beware of SQLAlchemy string representations
     db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'))
)


class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Interest {}>'.format(self.name)


milestones = db.Table('milestones',
    db.Column('milestone_id', db.Integer, db.ForeignKey('milestone.id')),
    db.Column('user_profile_id', db.Integer, db.ForeignKey('user_profile.id')),
)


class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Milestone {}>'.format(self.name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __init__(self, email):
        self.email = email
        # TODO Instantiate row with appropriate hash in UserProfile and UserHistory

    def __repr__(self):
        return '<User {}>'.format(self.email)


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hash = db.Column(db.String(255), unique=True)
    concentration_id = db.Column(db.Integer, db.ForeignKey('concentration.id'))
    gender = db.Column(db.String(10))
    ethnicity = db.Column(db.String(20))
    years_coding = db.Column(db.Float)
    year = db.Column(db.String(4))
    interests = db.relationship('Interest', secondary=interests,
                                backref=db.backref('user_profiles', lazy='dynamic'))
    # milestones = db.relationship('Milestone', secondary=milestones,
    #                              backref=db.backref('user_profiles'))

    def __init__(self, user_hash, concentration_id=None, year=None, years_coding=None, gender=None, ethnicity=None):
        self.user_hash = user_hash
        self.concentration_id = concentration_id
        self.year = year
        self.years_coding = years_coding
        self.gender= gender
        self.ethnicity = ethnicity

    def __repr__(self):
        return '<UserProfile {}>'.format(self.concentration)


class Concentration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    user_profiles = db.relationship('UserProfile', backref='concentration')

    def __init__(self, name):
        self.name = nameconuser

    def __repr__(self):
        return '<Concentration {}>'.format(self.name)


class Course(db.Model):
    # TODO add prerequisites = db.relationship('Course', backref='course', ...)
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)           # e.g. 1452974
    name_short = db.Column(db.String(20))  # e.g. CS164
    name_long = db.Column(db.String(255))  # e.g. Software Engineering
    description = db.Column(db.Text)
    course_histories = db.relationship('UserHistory',  backref='course')

    def __init__(self, code, name_short, name_long, description):
        self.code = code
        self.name_short = name_short
        self.name_long = name_long
        self.description = description

    def __repr__(self):
        return '<Course {} - {}>'.format(self.code, self.name_short)


class UserHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hash = db.Column(db.String(255), unique=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    grade = db.Column(db.String(3))
    hours = db.Column(db.Float)
    difficulty = db.Column(db.Integer)
    learning = db.Column(db.Integer)
    enjoyment = db.Column(db.Integer)

    def __init__(self, user_hash, course_id, semester_id, grade, hours, difficulty=None, learning=None, enjoyment=None):
        self.user_hash = user_hash
        self.course_id = course_id
        self.semester_id = semester_id
        self.grade = grade
        self.difficulty = difficulty
        self.learning = learning
        self.enjoyment = enjoyment

        def __repr__(self):
            return '<UserHistory {} {}>'.format(self.course_id, self.grade)


class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    course_histories = db.relationship('UserHistory', backref='semester')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Semester {}>'.format(self.name)
