from unittest import TestCase
import unittest
import json
from app import create_app, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import TestConfig
from flask_jwt_extended import create_access_token
from models.models import Shop, Product
from werkzeug.datastructures import FileStorage

class TestProductsRoutes(unittest.TestCase):

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
            response = cls.test_client.post('/accounts/signup', data=json.dumps(user_data),
                                            content_type='application/json')
            cls.assertTrue(response.status_code == 200, "Failed to create a test user")
            
            signin_data = {
                "email": "test@example.com",
                "password": "Password123"
            }
            response = cls.test_client.post('/accounts/signin', data=json.dumps(signin_data), content_type='application/json')
            cls.assertTrue(response.status_code == 200, "Failed to sign in")
            response_data = response.get_json()
            cls.access_token = response_data.get("access_token")
            headers = {'Authorization': f'Bearer {cls.access_token}'}
            shop_data = {
                "name": "hvjuhgvhjvj",
                "description": "string",
                "phone_number": "+380961122333",
                "link": "string"
                }
            response = cls.test_client.post('/shops/shop', data=json.dumps(shop_data),
                                        headers=headers, content_type='application/json')
    
    #create product
    def test_create_product_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "category_id": 1,
            "sub_category_name": "кризи",
            "product_name": "Test Product",
            "price": 20.0
        }

        response = self.test_client.post('/products/product', headers=headers,
                            data=json.dumps(product_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    #get info product
    def test_get_shop_products_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.test_client.get('/products/shop_products', headers=headers)
        self.assertEqual(response.status_code, 200)
        products = response.json
        found_product = any(product.get('product_name') == "Test Product" for product in products)
        self.assertTrue(found_product, "Test Product not found among shop products")

    #update product info
    def test_update_product_with_authenticated_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "product_name": "Updated Product",
            "product_description": "Updated Description",
            "price": 25.0,
            "product_characteristic": {"size": "small"}
        }

        with self.app.app_context():
            response = self.test_client.put('/products/update/1', headers=headers,
                                    data=json.dumps(product_data), content_type='application/json')
            self.assertEqual(response.status_code, 200)

            product_id = 1
            product = db.session.get(Product, product_id)
            found_product = product.product_name == "Updated Product"
            self.assertTrue(found_product, "Updated Product not found among shop products")

            response = self.test_client.delete('/products/deactivate/1', headers=headers)
            self.assertEqual(response.status_code, 200)

            product_id = 1
            product = db.session.get(Product, product_id)
            found_product = product.is_active is False
            self.assertTrue(found_product, "Updated Product not found among shop products")

    #not requirements field to create product
    def test_new_product_not_requirements(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "category_id": 1,
            "sub_category_name": "кризи",
            "price": 20.0
        }

        response = self.test_client.post('/products/product', headers=headers,
                            data=json.dumps(product_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    #user shop not have product id
    def test_update_product_with_other_user(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "product_name": "Updated Product",
            "product_description": "Updated Description",
            "price": 25.0,
            "product_characteristic": {"size": "small"}
        }

        with self.app.app_context():
            response = self.test_client.put('/products/update/2', headers=headers,
                                    data=json.dumps(product_data), content_type='application/json')
            self.assertEqual(response.status_code, 404)

    #product name not valid 
    def test_new_prod_name_not_valid(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "category_id": 1,
            "sub_category_name": "кризи",
            "product_name": "ы",
            "price": 20.0
        }

        response = self.test_client.post('/products/product', headers=headers,
                            data=json.dumps(product_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    #product description not valid 
    def test_new_prod_description_not_valid(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "category_id": 1,
            "sub_category_name": "кризи",
            "product_name": "New product",
            "product_description": "ы",
        }

        response = self.test_client.post('/products/product', headers=headers,
                            data=json.dumps(product_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    #sub_categories not enum
    def test_sub_categories_not_enum(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "category_id": 1,
            "sub_category_name": "криза",
            "product_name": "New product",
            "product_description": "product description",
        }

        response = self.test_client.post('/products/product', headers=headers,
                            data=json.dumps(product_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    #post not enum
    def test_post_not_enum(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "category_id": 1,
            "sub_category_name": "кризи",
            "product_name": "New product",
            "product_description": "product description",
            "delivery_post": "string"
        }

        response = self.test_client.post('/products/product', headers=headers,
                            data=json.dumps(product_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    #product status not enum
    def test_product_status_not_enum(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        product_data = {
            "category_id": 1,
            "sub_category_name": "кризи",
            "product_name": "New product",
            "product_description": "product description",
            "product_status": "string"
        }

        response = self.test_client.post('/products/product', headers=headers,
                            data=json.dumps(product_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    #not authenticated_user
    def test_get_shop_products_with_not_authenticated_user(self):
        response = self.test_client.get('/products/shop_products')
        self.assertEqual(response.status_code, 401)

    #get categories
    def test_get_categories(self):
        response = self.test_client.get('/categories/categories')
        self.assertEqual(response.status_code, 200)
    

if __name__ == '__main__':
    unittest.main()


