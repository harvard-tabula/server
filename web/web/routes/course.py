from web.routes import api
from web.models import db, Course, Concentration, Tag, Semester
from flask_restful import Resource
from flask_login import login_required


#
# Stateless (apart from session-based auth). These should return the same data regardless of who's authenticated.
#
class AllCourses(Resource):
    decorators = [login_required]

    def __init__(self):
        self.page_size = 20

    def get(self, page=1):
        count = db.session.query(Course).count()
        lix = (page - 1) * self.page_size + 1
        if lix > count:
            return {'state': 404, 'message': 'Out of courses'}
        num_courses = min(self.page_size, count - lix)
        rix = lix + num_courses - 1
        courses = db.session.query(Course).filter(lix <= Course.id, Course.id <= rix).all()
        result = {
            'state': 200,
            'message': 'Courses successfully retrieved.',
            'data': []
        }
        for course in courses:
            result['data'].append({
                                    'id': course.id,
                                    'catalog_number': course.name_short,
                                    'title': course.name_long,
                                    'description': course.description
                                   })

        return result


class Courses(Resource):
    decorators = [login_required]

    def get(self, course_id):

        course = db.session.query(Course).filter(Course.id == course_id).one_or_none()

        if not course:
            return {'state': 404, 'message': 'No course with that ID'}

        result = {
            'state': 200,
            'message': 'Course successfully retrieved.',
            'data': []
        }

        # Note: Because the other endpoints return resource relevant data in an array, I'm keeping the standard here.
        result['data'].append({
                                'id': course.id,
                                'catalog_number': course.name_short,
                                'title': course.name_long,
                                'description': course.description
                               })

        return result


class CourseSearch(Resource):  # TODO Search against concentration.synonym
    decorators = [login_required]

    def get(self, query):

        alias_map = {
            'cs': 'COMPSCI',
            'am': 'APMTH',
            'es': 'ENG-SCI',
        }

        tokens = query.split(' ')
        for i, token in enumerate(tokens):
            if token.lower() in alias_map:
                tokens[i] = alias_map[token.lower()]
        query = ' '.join(tokens)

        courses = set()

        res = db.session.query(Course).filter(
            Course.name_long.ilike('%{}%'.format(query)) |
            Course.name_short.ilike('%{}%'.format(query))
        ).limit(10)
        courses.update([course for course in res])

        result = {
            'state': 200,
            'message': 'Courses successfully retrieved.',
            'data': [
                {
                    'id': course.id,
                    'catalog_number': course.name_short,
                    'title': course.name_long,
                    'description': course.description
                }
                for course in courses
            ]
        }

        return result


class Tags(Resource):
    decorators = [login_required]

    def get(self):
        tags = db.session.query(Tag).all()
        result = [
            {
                "category": tag.category,
                "id": tag.id,
                "name": tag.name
            }
            for tag in tags
        ]

        return {'state': 200, 'message': 'Tags retrieved successfully', 'data': result}


class Concentrations(Resource):
    decorators = [login_required]

    def get(self):
        concentrations = db.session.query(Concentration).all()
        result = [
            {
                "id": concentration.id,
                "name": concentration.name
            }
            for concentration in concentrations
        ]

        return {'state': 200, 'message': 'Tags retrieved successfully', 'data': result}


class Semesters(Resource):
    decorators = [login_required]

    def get(self):
        semesters = db.session.query(Semester).all()
        result = [
            {
                "id": semester.id,
                "semester": '{} {}'.format(semester.term, semester.year)
            }
            for semester in semesters
        ]

        return {'state': 200, 'message': 'Tags retrieved successfully', 'data': result}


api.add_resource(AllCourses, '/allcourses', '/allcourses/page/<int:page>')
api.add_resource(Courses, '/courses/<int:course_id>')
api.add_resource(CourseSearch, '/coursesearch/<string:query>')
api.add_resource(Tags, '/tags')
api.add_resource(Concentrations, '/concentrations')
api.add_resource(Semesters, '/semesters')
