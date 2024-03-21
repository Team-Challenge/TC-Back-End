import csv
import os.path
from collections import namedtuple
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from pprint import pprint

import pytest
from flask import json
from sqlalchemy.orm import sessionmaker
from werkzeug.datastructures import FileStorage

from app import create_testing_app
from dependencies import db
from models.accounts import User
from models.products import Product, ProductDetail, ProductPhoto
from models.shops import Shop
from tests import status
from validation.products import get_subcategory_name

# TODO
# в json файли додати не валідні данні(кейси)
# створити окремі функції в поточному файлі для завантаження тих чи інших тестових сеймплів(з json файлів)


BASE_DIR = Path(__file__).resolve().parent.parent

N = 0

UserShopProductDetail = namedtuple('UserShopProductDetail', ['user', 'shop', 'product', 'detail'])

UserShop = namedtuple('UserShop', ['user', 'shop'])


class TestInvalidData:
    # todo fix server error when authorizing with token?
    # with this token i've received 500 error with login, but it expired now
    TEST_TOKEN = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNzEwODY0NjUxLCJqdGkiOiI5ODcwMDJhNi"
        "1mZWM2LTRlNDItYjM4MC02OTkzZWM1ZWM2NDIiLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoxLCJuYmYiOjE3MTA4NjQ2NTEsImV4cC"
        "I6MTcxMDg2NTU1MX0.FX4cS6C708nC8CoKsslWRZgX-X8gbj-gsCX8k0CQp08")


class TestValidData:
    # Accounts
    TEST_EMAIL = "test@mail.com"
    TEST_FULL_NAME = "TestName Full"
    TEST_PASSWORD = "123467898qweW"
    # Delivery User Info
    TEST_POST = '{"novaPost": true, "ukrPost": true}'
    TEST_CITY = "Kyiv"
    TEST_BRANCH_NAME = "Відділення 1"
    TEST_ADDRESS = "вул. Хрещатик, 1"
    # Shop info
    TEST_SHOP_NAME = "Shop name"
    TEST_SHOP_DESCRIPTION = "Best shop in the world"
    TEST_SHOP_PHONE_NUMBER = "+380000000000"
    TEST_SHOP_LINK = "instagram.tenet"
    # Product info
    TEST_CATEGORY_ID = 1
    TEST_SUB_CATEGORY_ID = 11
    TEST_SUB_CATEGORY_NAME = "Заколки"
    TEST_PRODUCT_NAME = "TestName Product"
    TEST_PRODUCT_DESCRIPTION = "TestDescription Product"
    # Product detail
    TEST_PRODUCT_IS_UNIQUE = False
    TEST_PRODUCT_IS_RETURN = True
    TEST_PRODUCT_PRICE = 25.91
    TEST_PRODUCT_CHARACTERISTIC = {
        "size": 35,
        "weight": 1
    }
    TEST_PRODUCT_DELIVERY_POST = {
        "novaPost": True,
        "ukrPost": False
    }

    TEST_PRODUCT_METHOD_OF_PAYMENT = {
        "cardPayment": True,
        "cashPayment": False,
        "securePayment": True
    }
    TEST_PRODUCT_STATUS = 'В наявності'

    # JSON variables
    JSON_TEST_PRODUCT_CHARACTERISTIC = json.dumps(TEST_PRODUCT_CHARACTERISTIC)
    JSON_TEST_PRODUCT_DELIVERY_POST = json.dumps(TEST_PRODUCT_DELIVERY_POST)
    JSON_TEST_PRODUCT_METHOD_OF_PAYMENT = json.dumps(TEST_PRODUCT_METHOD_OF_PAYMENT)

    # Files
    @classmethod
    def get_image(cls):
        return FileStorage(
            stream=BytesIO(b'file_mock'),
            filename='example.jpg',
            content_type='image/jpeg'
        )

    @classmethod
    def get_product_payload(cls, is_json=False, **kwargs):
        payload = {
            "category_id": cls.TEST_CATEGORY_ID,
            "sub_category_id": cls.TEST_SUB_CATEGORY_ID,
            "product_name": cls.TEST_PRODUCT_NAME,
            "product_description": cls.TEST_PRODUCT_DESCRIPTION,
            "is_active": True,
            "price": cls.TEST_PRODUCT_PRICE,
            "product_status": cls.TEST_PRODUCT_STATUS,
            "product_characteristic": cls.TEST_PRODUCT_CHARACTERISTIC if not is_json else cls.JSON_TEST_PRODUCT_CHARACTERISTIC,
            "is_return": cls.TEST_PRODUCT_IS_RETURN,
            "delivery_post": cls.TEST_PRODUCT_DELIVERY_POST if not is_json else cls.JSON_TEST_PRODUCT_DELIVERY_POST,
            "method_of_payment": cls.TEST_PRODUCT_METHOD_OF_PAYMENT if not is_json else cls.JSON_TEST_PRODUCT_METHOD_OF_PAYMENT,
            "is_unique": cls.TEST_PRODUCT_IS_UNIQUE
        }
        payload.update(**kwargs)
        return payload

    @classmethod
    def get_user_signin_payload(cls):
        return {"email": cls.TEST_EMAIL,
                "password": cls.TEST_PASSWORD}

    @classmethod
    def get_user_signup_payload(cls, **kwargs) -> dict:
        user_data = {"email": cls.TEST_EMAIL,
                     "full_name": cls.TEST_FULL_NAME,
                     "password": cls.TEST_PASSWORD}
        user_data.update(**kwargs)
        return user_data

    # @classmethod
    # def get_product_payload(cls) -> dict:
    #     return {
    #         "category_id": cls.TEST_CATEGORY_ID,
    #         "sub_category_id": cls.TEST_SUB_CATEGORY_ID,
    #         "product_name": cls.TEST_PRODUCT_NAME,
    #         "product_description": cls.TEST_PRODUCT_DESCRIPTION,
    #     }

    @classmethod
    def get_shop_payload(cls) -> dict:
        return {
            "name": cls.TEST_SHOP_NAME,
            "description": cls.TEST_SHOP_DESCRIPTION,
            "phone_number": cls.TEST_SHOP_PHONE_NUMBER,
            "link": cls.TEST_SHOP_LINK,
        }

    @classmethod
    def get_product_detail_payload(cls, product_id: int) -> dict:
        return {
            "product_id": product_id,
            "price": cls.TEST_PRODUCT_PRICE,
            "product_characteristic": cls.JSON_TEST_PRODUCT_CHARACTERISTIC,
            "delivery_post": cls.JSON_TEST_PRODUCT_DELIVERY_POST,
            "method_of_payment": cls.JSON_TEST_PRODUCT_METHOD_OF_PAYMENT
        }


def get_payload():
    # TODO
    # забрати глобальну змінну. Використовувати з функції описані вище
    global N
    N += 1
    payload = {
        "email": f"test_test@{N}example.com",
        "full_name": "Testname testlastname",
        "password": "Password123"
    }
    return payload


def create_test_user(email=TestValidData.TEST_EMAIL,
                     full_name=TestValidData.TEST_FULL_NAME,
                     password=TestValidData.TEST_PASSWORD) -> User:
    u = User.create_user(email, full_name, password)
    return u


def create_user_and_shop(session, email=TestValidData.TEST_EMAIL) -> UserShop:
    user = create_test_user(email=email)
    shop = Shop(owner_id=user.id, **TestValidData.get_shop_payload())
    session.add(shop)
    session.commit()
    session.refresh(shop)
    return UserShop(user, shop)


def create_user_shop_product(session) -> UserShopProductDetail:
    user, shop = create_user_and_shop(session)
    product = Product(shop_id=shop.id, **TestValidData.get_product_payload())
    session.add(product)
    session.commit()
    detail = ProductDetail(**TestValidData.get_product_detail_payload(product.id))
    session.add(detail)
    session.commit()
    session.refresh(product)
    session.refresh(detail)

    return UserShopProductDetail(user=user, shop=shop, product=product, detail=detail)


@contextmanager
def open_mock(filename: str):
    # Returns iterable rows as {key: value, key: value...}
    mock_path = os.path.join(Path(__file__).resolve().parent, "mocks/", filename)
    with open(mock_path) as file:
        yield csv.DictReader(file)


def authorize(client, refresh=False, **kwargs) -> dict:
    """Registers user and returns authorization header after successful signin"""
    valid_signup_data = TestValidData.get_user_signup_payload(**kwargs)
    client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                content_type='application/json')
    valid_signup_data.pop("full_name")
    valid_signin_data = valid_signup_data
    response = client.post('/accounts/signin', data=json.dumps(valid_signin_data),
                           content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get("access_token")

    # Authorization using token
    if refresh:
        access_token = response.get_json().get("refresh_token")
    else:
        access_token = response.get_json().get("access_token")
    headers = {'Authorization': f'Bearer {access_token}'}
    return headers


def orint(*args):
    print("\n-------------------------------------------")
    for arg in args:
        pprint(arg)
    print("-------------------------------------------")


@pytest.fixture()
def app():
    app = create_testing_app()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def engine(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield db.engine
        db.drop_all()


@pytest.fixture(scope='function')
def session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope='function')
def prepopulated_session(engine):
    session = sessionmaker(bind=engine)()
    users = []
    with open_mock("valid_users.csv") as data:
        for index, row in enumerate(data):
            row: dict
            if index == 0:
                # This function generates secret. Only first index, because of hashing
                User.create_user(**row)
            else:
                row.pop("password")
                user = User(**row)
                users.append(user)

    session.bulk_save_objects(users)
    session.flush()
    shops = []
    with open_mock("valid_shops.csv") as data:
        for index, row in enumerate(data):
            row: dict
            shop = Shop(**row)
            shop.owner_id = index + 1
            shops.append(shop)

    session.bulk_save_objects(shops)
    session.flush()

    product_photos = []
    with open_mock("valid_products.csv") as data:
        for row in data:
            row: dict
            product = Product(**row)
            session.add(product)
            session.flush()
            product_detail = ProductDetail(**TestValidData.get_product_detail_payload(product.id))
            product.sub_category_name = get_subcategory_name(row["category_id"],
                                                             row["sub_category_id"])
            product_detail.product_status = "В наявності"
            product_detail.delivery_post = TestValidData.TEST_POST
            product_detail.product_characteristic = row["product_characteristic"].replace("'", "\"")
            product.shop_id = 1

            session.add(product_detail)
            session.flush()
            product_photo = ProductPhoto(product_detail_id=product_detail.id,
                                         product_photo="sample.name",
                                         main=False)
            product_photos.append(product_photo)
    session.bulk_save_objects(product_photos)
    session.commit()
    yield session
    session.rollback()
    session.close()
