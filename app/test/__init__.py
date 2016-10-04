import unittest

from app import app
from app import clear_database, init_db


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        init_db()

    def tearDown(self):
        clear_database()
