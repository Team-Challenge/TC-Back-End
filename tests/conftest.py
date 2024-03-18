import csv
import os.path
from collections import namedtuple
from contextlib import contextmanager
from pathlib import Path

import pytest
from flask import json
from sqlalchemy.orm import sessionmaker

from app import create_testing_app
from config.config import TestConfig
from dependencies import db
from models.accounts import User
from models.products import Product, ProductDetail
from models.shops import Shop
from tests import status

# TODO
# в тестах не використовувати сеймпли із папки data +++++
# можна скопіювати json файли - покласти в парку tests/data
# в json файли додати не валідні данні(кейси)
# створити окремі функції в поточному файлі для завантаження тих чи інших тестових сеймплів(з json файлів)


BASE_DIR = Path(__file__).resolve().parent.parent

N = 0

UserShopProductDetail = namedtuple('UserShopProductDetail', ['user', 'shop', 'product', 'detail'])

UserShop = namedtuple('UserShop', ['user', 'shop'])


class TestValidData:
    # Accounts
    TEST_EMAIL = "test@mail.com"
    TEST_FULL_NAME = "TestName Full"
    TEST_PASSWORD = "123467898qweW"
    # Delivery User Info
    TEST_POST = "nova_post"
    TEST_CITY = "Kyiv"
    TEST_BRANCH_NAME = "Відділення 1"
    TEST_ADDRESS = "вул. Хрещатик, 1"
    # Shop info
    TEST_SHOP_NAME = "Shop name"
    TEST_SHOP_DESCRIPTION = "Best shop in the world"
    TEST_SHOP_PHONE_NUMBER = "+30991122333"
    TEST_SHOP_LINK = "instagram.tenet"
    # Product info
    TEST_CATEGORY_ID = 1
    TEST_SUB_CATEGORY_ID = 11
    TEST_SUB_CATEGORY_NAME = "Заколки"
    TEST_PRODUCT_NAME = "TestName Product"
    TEST_PRODUCT_DESCRIPTION = "TestDescription Product"
    # Product detail
    TEST_PRODUCT_PRICE = 25.91
    TEST_PRODUCT_CHARACTERISTIC = "Color: Blue"
    TEST_PRODUCT_DELIVERY_POST = "nova_post"
    TEST_PRODUCT_METHOD_OF_PAYMENT = "Card"

    @classmethod
    def get_user_signin_payload(cls):
        return {"email": cls.TEST_EMAIL,
                "password": cls.TEST_PASSWORD}

    @classmethod
    def get_user_signup_payload(cls) -> dict:
        return {"email": cls.TEST_EMAIL,
                "full_name": cls.TEST_FULL_NAME,
                "password": cls.TEST_PASSWORD}

    @classmethod
    def get_product_payload(cls) -> dict:
        return {
            "category_id": cls.TEST_CATEGORY_ID,
            "sub_category_id": cls.TEST_SUB_CATEGORY_ID,
            "product_name": cls.TEST_PRODUCT_NAME,
            "product_description": cls.TEST_PRODUCT_DESCRIPTION,
        }

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
            "product_characteristic": cls.TEST_PRODUCT_CHARACTERISTIC,
            "delivery_post": cls.TEST_PRODUCT_DELIVERY_POST,
            "method_of_payment": cls.TEST_PRODUCT_METHOD_OF_PAYMENT
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
    shop = Shop(owner_id=user.id, **TestValidData.get_product_payload())
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


def authorize(client, refresh=False) -> dict:
    # Registers user and returns authorization header after successful signin
    valid_signup_data = TestValidData.get_user_signup_payload()
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
        print(arg)
    print("-------------------------------------------")


@pytest.fixture()
def app():
    app = create_testing_app(config_class=TestConfig)
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
def prepopulated_engine(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture(scope='function')
def prepopulated_session(engine):
    session = sessionmaker(bind=engine)()
    users = []
    with open_mock("valid_users.csv") as data:
        for row in data:
            row: dict
            row.pop("password")
            user = User(**row)
            users.append(user)
    session.bulk_save_objects(users)
    session.commit()
    yield session
    session.rollback()
    session.close()
