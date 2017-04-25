from web import app, db, models
import pickle
import pandas


def load_courses(path):
    courses = pickle.load(open(path, 'rb'))
    for _, (harvard_id, dpt_id, description, name_long, name_short, prerequisites) in courses.iterrows():
        course = models.Course(int(harvard_id), name_short, name_long, description, int(dpt_id), prerequisites)
        db.session.add(course)
    db.session.commit()


def load_departments(path):
    departments = pickle.load(open(path, 'rb'))
    for department_id, (catalog_number, name) in departments.iterrows():
        department = models.Department(int(department_id), name, catalog_number)
        db.session.add(department)
    db.session.commit()


def load_concentrations(path):
    concentrations = pickle.load(open(path, 'rb'))
    for concentration_id, (name, ) in concentrations.iterrows():
        concentration = models.Concentration(int(concentration_id), name)
        db.session.add(concentration)
    db.session.commit()


def load_semesters():

    semesters = [(year, term) for term in [term for term in models.Term] for year in range(2004, 2030)]
    for semester in semesters:
        sem = models.Semester(semester[0], semester[1])
        db.session.add(sem)

    db.session.commit()


def load_tags():

    tags = {
        ('AI', 'academic'),
        ('Algorithms', 'academic'),
        ('Coding', 'academic'),
        ('Computational Biology', 'academic'),
        ('Computer Architecture', 'academic'),
        ('Computer Networking', 'academic'),
        ('Data Structures', 'academic'),
        ('Graphics', 'academic'),
        ('ML', 'academic'),
        ('Networks', 'academic'),
        ('Policy', 'academic'),
        ('Programming Languages', 'academic'),
        ('Robotics', 'academic'),
        ('Security', 'academic'),
        ('Systems', 'academic'),
        ('Consulting', 'professional'),
        ('Data Science', 'professional'),
        ('Design', 'professional'),
        ('DevOps', 'professional'),
        ('Finance', 'professional'),
        ('PM', 'professional'),
        ('SWE - Backend', 'professional'),
        ('SWE - Frontend', 'professional'),
        ('C', 'language'),
        ('C++ ', 'language'),
        ('Haskell', 'language'),
        ('JAVA', 'language'),
        ('JavaScript', 'language'),
        ('OCaml', 'language'),
        ('Python', 'language'),
        ('R', 'language'),
        ('Built a mobile app', 'milestone'),
        ('Built a server', 'milestone'),
        ('Built a web-app', 'milestone'),
        ('Created a model', 'milestone'),
        ('Proof-Based Math', 'milestone'),
        ('Love', 'user_history'),
        ('Happy', 'user_history'),
        ('Neutral', 'user_history'),
        ('Sad', 'user_history'),
        ('Angry', 'user_history'),
        ('Difficult', 'user_history'),
        ('Learning', 'user_history'),
        ('Easy', 'user_history'),
        ('Boring', 'user_history'),
    }

    for tag in tags:
        name, category = tag
        tag_to_add = models.Tag(name, category)
        db.session.add(tag_to_add)

    db.session.commit()


if __name__ == '__main__':

    """
    This script should never be used to drop or create tables. That's what Alembic is for. (Plus versioning and whatnot.)

    To get your DB to the correct state, run `python3 manage.py db upgrade` from the project directory.

    If you make changes to the schema, update the DB by first running `python3 manage.py db migrate -m <useful message>`
    before running the `upgrade` command again.

    See http://alembic.zzzcomputing.com/en/latest/tutorial.html if you're confused.
    """
    with app.app_context():
        load_semesters()
        load_tags()
        load_concentrations('./data/concentration_db.pkl')
        load_departments('./data/department_db.pkl')
        load_courses('./data/course_db.pkl')