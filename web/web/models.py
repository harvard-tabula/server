from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# Support for ENUMs between sqlalchemy, alembic, postgres is dodgy at best. Easier to do validation server-side.

Gender = [
    "Female",
    "Male",
    "Other"
]

Term = [
    "Spring",
    "Summer",
    "Fall",
    "Winter",
]

Grade = [
    "A",
    "A-",
    "B+",
    "B",
    "B-",
    "C+",
    "C",
    "C-",
    "D+",
    "D",
    "D-",
    "E+",
    "E",
    "S",
    "U",
    "P",
    "F",
    "W",
]

Ethnicity = [
    "Asian",
    "American Indian or Alaska Native",
    "Black or African American",
    "Latinx",
    "Native Hawaiian or Other Pacific Islander",
    "Other",
    "South Asian",
    "White",
]


Categories = [
    {"text": "Academic Interests", "category": "academic"},
    {"text": "Professional Interests", "category": "professional"},
    {"text": "Milestones", "category": "milestone"},
    {"text": "Languages", "category": "language"},
    {"text": "Class Experience", "category": "user_history"},
  ]


tags = db.Table('tags',
                # NB: Beware of SQLAlchemy string representations: UserProfile -> user_profile
                db.Column('user_profile_id', db.Integer, db.ForeignKey('user_profile.id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                )


course_tags = db.Table('course_tags',
                       db.Column('user_history_id', db.Integer, db.ForeignKey('user_history.id')),
                       db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                       )


class Tag(db.Model):
    constraint = db.UniqueConstraint('name', 'category')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(20))

    def __init__(self, id, name, category):
        self.id = id
        self.name = name
        self.category = category

    def __repr__(self):
        return '<Tag type={} name={}>'.format(self.category, self.name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __init__(self, email, name, avatar):
        self.email = email
        self.name = name
        self.avatar = avatar

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):  # User is allowed to authenticate
        return True  # TODO Should this be the default value?

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.email)


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hash = db.Column(db.String(255), unique=True, nullable=False)
    concentration_id = db.Column(db.Integer, db.ForeignKey('concentration.id'))
    gender = db.Column(db.String(6))
    ethnicity = db.Column(db.String(15))
    years_coding = db.Column(db.Float)
    year = db.Column(db.String(4))
    tags = db.relationship('Tag', secondary=tags, cascade="all",
                           backref=db.backref('user_profiles', lazy='dynamic'))

    def __init__(self, user_hash, concentration_id=None, year=None, years_coding=None, gender=None, ethnicity=None):
        self.user_hash = user_hash
        self.concentration_id = concentration_id
        self.year = year
        self.years_coding = years_coding
        self.gender = gender
        self.ethnicity = ethnicity

    def __repr__(self):
        return '<UserProfile id={}>'.format(self.id)


class Concentration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    constraint = db.UniqueConstraint('name')
    name = db.Column(db.String(255))
    user_profiles = db.relationship('UserProfile', backref='concentration')

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<Concentration name={}>'.format(self.name)


class Department(db.Model):
    constraint = db.UniqueConstraint('name, catalog_number')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    catalog_number = db.Column(db.String(30))
    courses = db.relationship('Course', backref='department')

    def __init__(self, id, name, catalog_number):
        self.id = id
        self.name = name
        self.catalog_number = catalog_number

    def __repr__(self):
        return '<Department name={}>'.format(self.name)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    harvard_id = db.Column(db.Integer)     # e.g. 1452974
    name_short = db.Column(db.String(20))  # e.g. COMPSCI 164
    name_long = db.Column(db.String(255))  # e.g. Software Engineering
    description = db.Column(db.Text)
    course_histories = db.relationship('UserHistory',  backref='course')
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    prerequisites = db.Column(db.Text)

    def __init__(self, id, harvard_id, name_short, name_long, description, department_id, prerequisites):
        self.id = id
        self.harvard_id = harvard_id
        self.name_short = name_short
        self.name_long = name_long
        self.description = description
        self.department_id = department_id
        self.prerequisites = prerequisites

    def __repr__(self):
        return '<Course name={}>'.format(self.name_short)


class UserHistory(db.Model):

    constraint = db.UniqueConstraint('user_hash', 'course_id', 'semester_id')
    id = db.Column(db.Integer, primary_key=True)
    user_hash = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    grade = db.Column(db.String(5))
    hours = db.Column(db.Integer)
    course_tags = db.relationship('Tag', secondary=course_tags, cascade="all",
                           backref=db.backref('user_histories', lazy='dynamic'))

    def __init__(self, user_hash, course_id, semester_id, grade, hours=None):
        self.user_hash = user_hash
        self.course_id = course_id
        self.semester_id = semester_id
        self.hours = hours
        self.grade = grade

    def __repr__(self):
        return '<UserHistory id={}>'.format(self.course_id)


class Semester(db.Model):

    constraint = db.UniqueConstraint('term', 'year')
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(6))
    year = db.Column(db.String(4))
    course_histories = db.relationship('UserHistory', backref='semester')

    def __init__(self, id, year, term):
        self.id = id
        self.year = year
        self.term = term

    def __repr__(self):
        return '<Semester term={} year={}>'.format(self.year, self.term)
