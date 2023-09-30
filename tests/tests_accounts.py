import unittest
from app import create_app, db
from models.users import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from config.config import TestConfig


class TestAccountsRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        
        cls.app = create_app(config_class=TestConfig)
        cls.app.testing = True
        cls.test_client = cls.app.test_client()
        
        
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)

        
        with cls.app.app_context():
            db.create_all()

    def setUp(self):
        
        self.session = self.Session()
    

    def test_valid_signup_and_verify_and_signin_and_logout(self):
        #signup
        valid_signup_data = {
            "email": "test@example.com",
            "full_name": "Test_name test_last_name",
            "password": "password123"
        }

        response = self.test_client.post('/accounts/signup', data=json.dumps(valid_signup_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        #verify
        token = response.get_json().get('link')

        response = self.test_client.get(f'/accounts/verify/{token}')
        self.assertEqual(response.status_code, 200)
        bed_token = "bed_token"
        response = self.test_client.get(f'/accounts/verify/{bed_token}')
        self.assertEqual(response.status_code, 404)

        #signin
        valid_signin_data = {
            "email": "test@example.com",
            "password": "password123"
        }

        response = self.test_client.post('/accounts/signin', data=json.dumps(valid_signin_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        
        response_data = response.get_json()
        self.assertIn("access_token", response_data)
        self.assertIn("refresh_token", response_data)

        #update user full name and phone number
        access_token = response.get_json().get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}

        valid_update_user_data = {
            "full_name": "Test Update",
            "phone_number": "+380972323233"
        }
        response = self.test_client.post('/accounts/update_user', data=json.dumps(valid_update_user_data), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)

        #logout
        response = self.test_client.delete('/accounts/logout', headers=headers)

        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get('msg'), 'Access token successfully revoked')


    def test_invalid_email_signup(self):

        invalid_email_data = {
            "email": "",
            "full_name": "John Doe",
            "password": "password123"
        }

        response = self.test_client.post('/accounts/signup', data=json.dumps(invalid_email_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_password_signup(self):

        invalid_password_data = {
            "email": "test0@example.com",
            "full_name": "John Doe",
            "password": "pa01"
        }

        response = self.test_client.post('/accounts/signup', data=json.dumps(invalid_password_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_fullname_signup(self):

        invalid_fullname_data = {
            "email": "test0@example.com",
            "full_name": "",
            "password": "pa0123456"
        }

        response = self.test_client.post('/accounts/signup', data=json.dumps(invalid_fullname_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_form_signup(self):

        invalid_form_data = {
            "password": "212122121fhhfh"
        }

        response = self.test_client.post('/accounts/signup', data=json.dumps(invalid_form_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)


    def test_invalid_signin(self):
        
        invalid_signin_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }

        response = self.test_client.post('/accounts/signin', data=json.dumps(invalid_signin_data), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_invalid_form_signin(self):
        
        invalid_signin_data = {
        }

        response = self.test_client.post('/accounts/signin', data=json.dumps(invalid_signin_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)



if __name__ == '__main__':
    unittest.main()










