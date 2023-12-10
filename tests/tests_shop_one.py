import unittest
from app import create_app, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from config.config import TestConfig
from flask_jwt_extended import create_access_token

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
        
        def test_create_shop_with_not_authenticated_user(self):

            shop_data = {
                "name": "My Test Shop",
                "description": "Test Shop Description",
                "phone_number": "+380551122333",
                "link": "http://mytestshop.com"
            }

            response = self.test_client.post('/shops/shop', data=json.dumps(shop_data))
            self.assertEqual(response.status_code, 401)
    
    def test_get_shop_shop_photo_with_not_authenticated_user(self):

        response = self.test_client.get('/shops/shop_photo')
        
        self.assertEqual(response.status_code, 401)

    def test_post_shop_shop_photo_with_not_authenticated_user(self):
      
        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            response = self.test_client.post('/shops/shop_photo', data={'image': image_file})
        
        self.assertEqual(response.status_code, 401)

    def test_delete_shop_shop_photo_with_not_authenticated_user(self):
       
        response = self.test_client.delete('/shops/shop_photo')
        
        self.assertEqual(response.status_code, 401)

    def test_get_shop_shop_banner_with_not_authenticated_user(self):

        response = self.test_client.get('/shops/shop_banner')
        
        self.assertEqual(response.status_code, 401)

    def test_post_shop_shop_banner_with_not_authenticated_user(self):
     
        with open('tests/test_images/alf.jpg', 'rb') as image_file:
                response = self.test_client.post('/shops/shop_banner', data={'image': image_file})
        
        self.assertEqual(response.status_code, 401)

    def test_delete_shop_shop_banner_with_not_authenticated_user(self):
        
        response = self.test_client.delete('/shops/shop_banner')
        
        self.assertEqual(response.status_code, 401)

    def test_get_shop_shop_info_with_not_authenticated_user(self):
     
        response = self.test_client.get('/shops/shop_info')
        
        self.assertEqual(response.status_code, 401)

    # Authenticated user
    # Not name in request
    def test_create_shop_phone_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'applicationjson'}

        shop_data = {
            "description": "Test Shop Description",
            "phone_number": "+380123456789",
            "link": "http://mytestshop.com"
        }

        response = self.test_client.post('/shops/shop', data=json.dumps(shop_data),headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("error", response_data)

        self.assertEqual(response.status_code, 400)

    # Not phone in request
    def test_create_shop_name_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type':'applicationjson'}

        shop_data = {
                "name": "Test Shop name",
                "phone_number": "+380123456789",
                "link": "http://mytestshop.com"}

        response = self.test_client.post('/shops/shop', data=json.dumps(shop_data),    headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("error", response_data)

        self.assertEqual(response.status_code, 400)

    # Not shop, user is authorization
    def test_get_shop_photo_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        response = self.test_client.get('/shops/shop_photo',headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("message", response_data)
        self.assertIn("There is no store by user", response_data)

        self.assertEqual(response.status_code, 404)

    def test_post_shop_photo_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            response = self.test_client.post('/shops/shop_photo', headers=headers, data={'image': image_file})

        response_data = response.data.decode('utf-8')

        self.assertIn("message", response_data)
        self.assertIn("There is no store by user", response_data)

        self.assertEqual(response.status_code, 404)

    def test_delete_shop_photo_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        response = self.test_client.delete('/shops/shop_photo',headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("message", response_data)
        self.assertIn("There is no store by user", response_data)

        self.assertEqual(response.status_code, 404)

    def test_put_shop_photo_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            response = self.test_client.put('/shops/shop_photo', headers=headers, data={'image': image_file})

        response_data = response.data.decode('utf-8')
        self.assertIn("Method Not Allowed", response_data)

        self.assertEqual(response.status_code, 405)

    def test_get_shop_banner_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        response = self.test_client.get('/shops/shop_banner',headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("There is no store by user", response_data)
        self.assertEqual(response.status_code, 404)

    def test_post_shop_banner_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            response = self.test_client.post('/shops/shop_banner', headers=headers, data={'image': image_file})

        response_data = response.data.decode('utf-8')
        self.assertIn("There is no store by user", response_data)
        self.assertEqual(response.status_code, 404)

    def test_delete_shop_banner_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        response = self.test_client.delete('/shops/shop_banner',headers=headers)
        response_data = response.data.decode('utf-8')
        self.assertIn("There is no store by user", response_data)
        self.assertEqual(response.status_code, 404)

    def test_put_shop_banner_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        with open('tests/test_images/alf.jpg', 'rb') as image_file:
            response = self.test_client.put('/shops/shop_banner', headers=headers, data={'image': image_file})

        response_data = response.data.decode('utf-8')
        self.assertIn("Method Not Allowed", response_data)
        self.assertEqual(response.status_code, 405)

    def test_get_shop_info_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        response = self.test_client.get('/shops/shop_info',headers=headers)
        response_data = response.data.decode('utf-8')

        self.assertIn("There is no store by user", response_data)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()