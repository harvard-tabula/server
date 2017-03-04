from web import app, db, models
import csv


def load_courses(path):
    with open(path) as f:
        f.readline()
        reader = csv.reader(f)
        for row in reader:
            course = models.Course(row[4], row[3], row[0], row[1], row[2])
            db.session.add(course)
    db.session.commit()

if __name__ == '__main__':
    load_courses('../data/course_table.csv')
