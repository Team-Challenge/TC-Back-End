import unittest
from app import create_app, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from config.config import TestConfig
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import FileStorage

class TestShopsRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config_class=TestConfig)
        cls.app.testing = True
        cls.test_client = cls.app.test_client()

        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)

        with cls.app.app_context():
            db.create_all()

            user_data = {
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "Password123"
            }
            response = cls.test_client.post('/accounts/signup', data=json.dumps(user_data), content_type='application/json')
            cls.assertTrue(response.status_code == 200, "Failed to create a test user")
            
            signin_data = {
                "email": "test@example.com",
                "password": "Password123"
            }
            response = cls.test_client.post('/accounts/signin', data=json.dumps(signin_data), content_type='application/json')
            cls.assertTrue(response.status_code == 200, "Failed to sign in")
            response_data = response.get_json()
            cls.access_token = response_data.get("access_token")

    # create shop
    def test_create_shop_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

        shop_data = {
                        "name": "name shop",
                        "phone_number": "+380123456789"
                    }

        response = self.test_client.post('/shops/shop', data=json.dumps(shop_data),headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("Shop created successfully", response_data)
        self.assertEqual(response.status_code, 201)

    # udate shop
    def test_update_shop_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

        shop_data = {
                        "description": "description shop",
                        "link": "@insta"
                    }

        response = self.test_client.post('/shops/shop', data=json.dumps(shop_data),headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("Shop details updated successfully", response_data)
        self.assertEqual(response.status_code, 200)

    # update bad name
    def test_update_shop_bad_name_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

        shop_data = {
                        "name": "N"
                    }

        response = self.test_client.post('/shops/shop', data=json.dumps(shop_data),headers=headers)
        response_data = response.data.decode('utf-8')
        self.assertIn(response_data)
        self.assertIn("Invalid shop name format", response_data)
        self.assertEqual(response.status_code, 400)

    # update bad phone
    def test_update_shop_bad_phone_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

        shop_data = {
                        "phone_number": "+38063454"
                    }

        response = self.test_client.post('/shops/shop', data=json.dumps(shop_data),headers=headers)
        response_data = response.data.decode('utf-8')
        self.assertIn("error", response_data)
        self.assertIn("Invalid phone number format. Must start with +380 and have 9 digits.", response_data)
        self.assertEqual(response.status_code, 400)

    def test_get_shop_info_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        response = self.test_client.get('/shops/shop_info',headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("banner_shop", response_data)
        self.assertIn("description", response_data)
        self.assertIn("id", response_data)
        self.assertIn("link", response_data)
        self.assertIn("name", response_data)
        self.assertIn("owner", response_data)
        self.assertIn("phone_number", response_data)
        self.assertIn("photo_shop", response_data)
        self.assertEqual(response.status_code, 200)

    def test_create_get_delete_photo(self):
        # create
        headers = {'Authorization': f'Bearer {self.access_token}'}
        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            file_storage = FileStorage(image_file, content_type='image/jpeg', name='image.jpg')
            response = self.test_client.post('/shops/shop_photo', headers=headers, data= {'image':    file_storage})

        # get
        response = self.test_client.get('/shops/shop_photo', headers=headers)
        self.assertEqual(response.status_code, 200)

        # put
        response = self.test_client.put('/shops/shop_photo', headers=headers)
        self.assertEqual(response.status_code, 405)

        # delete
        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            file_storage = FileStorage(image_file, content_type='image/jpeg', name='image.jpg')
            response = self.test_client.delete('/shops/shop_photo', headers=headers, data= {'image':    file_storage})
        

    def test_ycreate_get_delete_banner(self):
        # create
        headers = {'Authorization': f'Bearer {self.access_token}'}

        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            file_storage = FileStorage(image_file, content_type='image/jpeg', name='image.jpg')
            response = self.test_client.post('/shops/shop_banner', headers=headers, data={'image': file_storage})

        self.assertEqual(response.status_code, 200)

        # get
        response = self.test_client.get('/shops/shop_banner', headers=headers)
        self.assertEqual(response.status_code, 200)

        # put
        response = self.test_client.put('/shops/shop_banner', headers=headers)
        self.assertEqual(response.status_code, 405)

        # delete
        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            file_storage = FileStorage(image_file, content_type='image/jpeg', name='image.jpg')
            response = self.test_client.delete('/shops/shop_banner', headers=headers, data={'image':    file_storage})



if __name__ == '__main__':
    unittest.main()