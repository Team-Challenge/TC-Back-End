import unittest
from api.dao.userDao import UserDao
import sqlite3

class TestUserDAO(unittest.TestCase):

    def setUp(self):
        con = sqlite3.connect('/home/oranwela/apps/TC-Back-End/api/app.db')
        self.assertIsNot(con, 0)
        

    def tearDown(self):
        pass

    def test_create_user(self):
        pass

    def test_get_user_by_username(self):
        pass

if __name__ == '__main__':
    unittest.main()
