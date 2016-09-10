import logging
import logging.config
import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail

import json

env = os.environ.get('FLASK_ENV', 'development')

app = Flask(__name__, static_folder="static")
app.config.from_pyfile('../config/config.py')

# setup logging
with open('config/logging-%s.yaml' % env) as f:
    import yaml
    logging.config.dictConfig(yaml.load(f))


db = SQLAlchemy(app)
# Define naming constraints so that Alembic just works
# See http://docs.sqlalchemy.org/en/rel_0_9/core/constraints.html#constraint-naming-conventions
db.metadata.naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
migrate = Migrate(app, db, transaction_per_migration=True)
csrf = CsrfProtect(app)
mail = Mail(app)


UPLOAD_PATH = app.config['UPLOAD_PATH']
if not os.path.isdir(UPLOAD_PATH):
    os.mkdir(UPLOAD_PATH)


# override flask mail's send operation to inject some customer headers
original_send = mail.send
def send_email_with_sendgrid(message):
    extra_headers = {
        "filters": {
            "templates": {
                "settings": {
                    "enable": "1",
                    "template_id": app.config['SENDGRID_TRANSACTIONAL_TEMPLATE_ID']
                }
            },
            "ganalytics": {
                "settings": {
                    "enable": "1",
                    "utm_medium": "email",
                    "utm_source": "transactional",
                    "utm_campaign": "user-account"
                }
            }
        }
    }
    message.extra_headers = {
        'X-SMTPAPI': json.dumps(extra_headers)
    }
    original_send(message)
app.extensions.get('mail').send = send_email_with_sendgrid


# setup assets
from flask.ext.assets import Environment, Bundle
assets = Environment(app)
assets.url_expire = False
assets.debug      = app.debug
# source files
assets.load_path  = ['%s/static' % app.config.root_path]

from webassets.filter.pyscss import PyScss

assets.register('css',
    Bundle(
      'font-awesome-4.2.0/css/font-awesome.min.css',
      'chosen/chosen.min.css',
      Bundle(
        'resources/css/style.scss',
        'resources/css/bill-progress.scss',
        filters=PyScss(load_paths=assets.load_path),
        output='stylesheets/styles.%(version)s.css'),
      output='stylesheets/app.%(version)s.css'))

assets.register('admin-css',
    Bundle(
      'font-awesome-4.2.0/css/font-awesome.min.css',
      Bundle(
        'resources/css/admin.scss',
        filters=PyScss(load_paths=assets.load_path),
        output='stylesheets/admin-styles.%(version)s.css'),
      output='stylesheets/admin.%(version)s.css'))

assets.register('js', Bundle(
    'bower_components/jquery/dist/jquery.min.js',
    'bower_components/bootstrap-sass/assets/javascripts/bootstrap.min.js',
    'chosen/chosen.jquery.js',
    'resources/javascript/committees.js',
    'resources/javascript/users.js',
    'resources/javascript/members.js',
    'resources/javascript/pmg.js',
    output='javascript/app.%(version)s.js'))

assets.register('admin-js', Bundle(
    'resources/javascript/admin/admin.js',
    'resources/javascript/admin/email_alerts.js',
    output='javascript/admin.%(version)s.js'))


# background tasks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from threading import Thread
scheduler = BackgroundScheduler({
    'apscheduler.jobstores.default': SQLAlchemyJobStore(engine=db.engine),
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '2',
    },
    'apscheduler.timezone': 'UTC',
})
if app.config['RUN_PERIODIC_TASKS']:
    scheduler.start()

# if we don't do this in a separate thread, we hang trying to connect to the db
import pmg.tasks
Thread(target=pmg.tasks.schedule).start()


import helpers
import views
import user_management
import admin

from pmg.api import api
app.register_blueprint(api, subdomain='api')
