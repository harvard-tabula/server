from web import app, db, models
import csv


def load_courses(path):
    with open(path, encoding='latin') as f:
        f.readline()
        reader = csv.reader(f)
        for row in reader:
            course_id = int(row[4])
            name_short = row[3]
            name_long = row[0]
            description = row[1]
            dpt_id = int(row[2])
            course = models.Course(course_id, name_short, name_long, description, dpt_id)
            db.session.add(course)
    db.session.commit()


def load_concentrations(path):
    with open(path, encoding='latin') as f:
        f.readline()
        reader = csv.reader(f)
        for row in reader:
            dpt_id = int(row[0])
            name = row[1]
            group_code = row[2]
            course = models.Concentration(dpt_id, name, group_code)
            db.session.add(course)
    db.session.commit()

if __name__ == '__main__':
    load_concentrations('./data/departments.csv')
    load_courses('./data/course_table.csv')
