import os

# setup testing environment before anything imports app
os.environ["FLASK_ENV"] = "test"
from pmg import app
from pmg.models import db

from flask_testing import TestCase, LiveServerTestCase
import multiprocessing
import time
import urllib2


class PMGTestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class PMGLiveServerTestCase(LiveServerTestCase):
    def __call__(self, result=None):
        """
        Does the required setup, doing it here means you don't have to
        call super.setUp in subclasses.
        """

        # Get the app
        self.app = self.create_app()
        self.port = self.app.config.get("LIVESERVER_PORT", 5000)

        # We need to create a context in order for extensions to catch up
        self._ctx = self.app.test_request_context()
        self._ctx.push()

        try:
            self._spawn_live_server()
            super(LiveServerTestCase, self).__call__(result)
        finally:
            self._post_teardown()
            self._terminate_live_server()

    def _spawn_live_server(self):
        self._process = None

        worker = lambda app, port: app.run(port=port, use_reloader=False, threaded=True)

        self._process = multiprocessing.Process(
            target=worker, args=(self.app, self.port)
        )

        self._process.start()

        # We must wait for the server to start listening, but give up
        # after a specified maximum timeout
        timeout = self.app.config.get("LIVESERVER_TIMEOUT", 5)
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                raise RuntimeError(
                    "Failed to start the server after %d seconds. " % timeout
                )

            if self._can_ping_server():
                break

    def create_app(self):
        # https://stackoverflow.com/a/38529331/1305080
        db.engine.dispose()
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def get_page_contents(self, url):
        response = urllib2.urlopen(url)
        self.assertEqual(200, response.code)
        self.html = response.read()

    def get_page_contents_as_user(self, user, url):
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = user.id
                session['fresh'] = True

            response = client.get(url, follow_redirects=True)
            self.assertEqual(200, response.status_code)
            self.html = response.data