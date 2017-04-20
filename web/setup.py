from setuptools import setup

setup(
    name='Tabula Server',
    version='0.0',
    packages=['web'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask==0.12',
        'psycopg2==2.6.2',
        'SQLAlchemy==1.1.5',
        'Flask-SQLAlchemy==2.1',
        'Flask-Migrate==2.0.3',
        'flask-restful==0.3.5',
        'requests-oauthlib==0.8.0',
        'flask-login==0.4.0',
        'flask-cors==3.0.2',
        'uwsgi',
        'pandas',
    ],
)
