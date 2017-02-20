from . import db


# interests = db.Table('interests',
#     db.Column('interest_id', db.Integer, db.ForeignKey('interest.id')),
#     db.Column('user_profile_id', db.Integer, db.ForeignKey('userprofile.id')),
# )


# class Interest(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), unique=True)
#     description = db.Column(db.Text)


# milestones = db.Table('milestones',
#     db.Column('milestone_id', db.Integer, db.ForeignKey('milestone.id')),
#     db.Column('user_profile_id', db.Integer, db.ForeignKey('userprofile.id')),
#     db.PrimaryKeyConstraint('milestone_id', 'user_profile_id'),
#     db.ForeignKeyConstraint(['user_profile_id'], ['userprofile.id'])
# )


# class Milestone(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), unique=True)
#     description = db.Column(db.Text)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)

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
    # interests = db.relationship('Interest', secondary=interests,
    #                             backref=db.backref('user_profiles'))
    # milestones = db.relationship('Milestone', secondary=milestones,
    #                              backref=db.backref('user_profiles'))


class Concentration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    user_profiles = db.relationship('UserProfile', backref='concentration')


class Course(db.Model):
    # TODO add prerequisites = db.relationship('Course', backref='course', ...)
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)           # e.g. 1452974
    name_short = db.Column(db.String(20))  # e.g. CS164
    name_long = db.Column(db.String(255))  # e.g. Software Engineering
    description = db.Column(db.Text)
    course_histories = db.relationship('UserHistory',  backref='course')


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


class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    course_histories = db.relationship('UserHistory', backref='semester')
