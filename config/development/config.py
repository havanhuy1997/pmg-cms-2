DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/tmp.db'
SECRET_KEY = "AEORJAEONIAEGCBGKMALMAENFXGOAERGN"
API_HOST = "http://localhost:5001/"
FRONTEND_HOST = "http://localhost:5000/"
RESULTS_PER_PAGE = 50

STATIC_HOST = "http://eu-west-1-pmg.s3-website-eu-west-1.amazonaws.com/"
ES_SERVER = "http://ec2-54-77-69-243.eu-west-1.compute.amazonaws.com:9200"
S3_BUCKET = "eu-west-1-pmg"
UPLOAD_PATH = "/tmp/pmg_upload/"