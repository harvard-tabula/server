from web import app, db, models
import pickle
import pandas


def create_or_update(model, **kwargs):
    """
    NB: This function assumes that the ID for a given logical entity in the DB will not change over time! i.e. do not
    change the order of things below.

    It also assumes that everything we add to the DB manually will set its own ID explicitly. Do not break that invariant
    or sad things will happen.

    However, feel free to update text if necessary. (That's the whole point.)
    """
    base_query = db.session.query(model).filter_by(id=kwargs['id'])
    if not base_query.one_or_none():
        instance = model(**kwargs)
        db.session.add(instance)
    else:
        base_query.update(dict(**kwargs))


def load_courses(path):
    courses = pickle.load(open(path, 'rb'))
    for course_id, (harvard_id, dpt_id, description, name_long, name_short, prerequisites) in courses.iterrows():
        create_or_update(
            models.Course,
            id=int(course_id),
            harvard_id=int(harvard_id),
            department_id=int(dpt_id),
            name_short=name_short,
            name_long=name_long,
            prerequisites=prerequisites,
            description=description,
        )
    db.session.commit()


def load_departments(path):
    departments = pickle.load(open(path, 'rb'))
    for department_id, (catalog_number, name) in departments.iterrows():
        create_or_update(
            models.Department,
            id=int(department_id),
            name=name,
            catalog_number=catalog_number,
        )
    db.session.commit()


def load_concentrations(path):
    concentrations = pickle.load(open(path, 'rb'))
    for concentration_id, (name, ) in concentrations.iterrows():
        create_or_update(
            models.Concentration,
            id=int(concentration_id),
            name=name,
        )
    db.session.commit()


def load_semesters():

    semesters = [(year, term) for term in [term for term in models.Term] for year in range(2004, 2030)]
    for semester_id, (year, term) in enumerate(semesters):
        create_or_update(models.Semester, id=semester_id, year=str(year), term=term)
    db.session.commit()


def load_tags():

    tags = [
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
    ]

    for tag_id, (name, category) in enumerate(tags):
        create_or_update(models.Tag, id=tag_id, name=name, category=category)
    db.session.commit()


if __name__ == '__main__':

    """
    Key assumption: Data being loaded via this script is more up to date than any data on the DB. i.e. if some similar object
    already exists in the DB, the script assumes that the one being inserted is more valid even if it contains "less" information.

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
