from os import environ as env

SQLALCHEMY_DATABASE_URI = env['SQLALCHEMY_DATABASE_URI']
SECRET_KEY = "AEORJAEONIAEGCBGKMALMAENFXGOAERGN"
API_HOST = "http://api.pmg.org.za/"
FRONTEND_HOST = "http://new.pmg.org.za/"
RESULTS_PER_PAGE = 20

STATIC_HOST = "http://eu-west-1-pmg.s3-website-eu-west-1.amazonaws.com/"
