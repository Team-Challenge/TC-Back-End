from unittest.mock import patch

import pytest
from flask import json

from tests import status

from models.products import Product, ProductDetail
from tests.conftest import (authorize, create_user_and_shop, TestValidData,
                            create_user_shop_product)

create_product_negative_payload = [
    {
        "category_id": 1,
        "sub_category_id": 11,
        "product_name": "new product",
        "product_description": "new product description",
        "product_status": "В наявності"
    },
    {
        "category_id": 1,
        "sub_category_id": 11,
        "product_name": "new product",
        "product_description": "new product description",
        "price": 1500,
        "product_status": "Наявний"
    },
    {
        "category_id": 2,
        "sub_category_id": 11,
        "product_name": "new product",
        "product_description": "new product description",
        "price": 1500,
        "product_status": "В наявності"
    },
    {
        "category_id": 1,
        "sub_category_id": 11,
        "product_name": "new productы",
        "product_description": "new product descriptionы",
        "price": 1500,
        "product_status": "В наявності"
    },
    {
        "category_id": 40,
        "sub_category_id": 11,
        "product_name": "new productы",
        "product_description": "new product descriptionы",
        "price": 1500,
        "product_status": "В наявності"
    }
]

update_product_negative_payload = [
    {
        "product_name": "new productё",
        "product_description": "new product description",
        "product_status": "В наявності"
    },
    {
        "product_name": "new product",
        "product_description": "new product description",
        "price": 1500,
        "product_status": "Наявний"
    },
    {

        "product_name": "new product",
        "product_description": "ёnew product description",
        "price": 1500,
        "product_status": "В наявності"
    },
    {
        "product_status": "Є",
    },
    {
        "is_return": "Так",
    }
]


def test_create_product_success_1(client, prepopulated_session):
    """Test create new product products using prepopulated user data"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")
    payload = {
        "category_id": 1,
        "sub_category_id": 11,
        "product_name": "new product",
        "product_description": "new product description",
        "is_active": True,
        "price": 1500,
        "product_status": "В наявності",
        "product_characteristic": {
            "size": "4",
            "weight": "51",
            "color": "blue",
            "materials": "metal",
        },
        "is_return": True,
        "delivery_post": {
            "novaPost": True,
            "ukrPost": False
        },
        "method_of_payment": {
            "cardPayment": True,
            "cashPayment": False,
            "securePayment": True
        },
        "is_unique": False
    }

    # When
    with client:
        response = client.post("/products/product", data=json.dumps(payload),
                               content_type='application/json', headers=headers)

        # Then
        assert response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.get_json().get('product_id') is not None

        # After
        product_id = response.get_json().get('product_id')
        response = client.get(f"/products/product_info/{product_id}")
        assert response.status_code == status.HTTP_200_OK

        # Check each field of the product
        assert response.get_json().get('category_id') == payload["category_id"]
        assert response.get_json().get("sub_category_id") == payload["sub_category_id"]
        assert response.get_json().get("product_name") == payload["product_name"]
        assert response.get_json().get("product_description") == payload["product_description"]
        assert response.get_json().get("is_active") == payload["is_active"]
        assert response.get_json().get("price") == payload["price"]
        assert response.get_json().get("product_status") == payload["product_status"]
        assert response.get_json().get("product_characteristic") == payload[
            "product_characteristic"]
        assert response.get_json().get("is_return") == payload["is_return"]
        assert response.get_json().get("delivery_post") == payload["delivery_post"]
        assert response.get_json().get("method_of_payment") == payload["method_of_payment"]
        assert response.get_json().get("is_unique") == payload["is_unique"]
        assert response.get_json().get("shop_id") is not None
        assert response.get_json().get("id") is not None
        assert response.get_json().get("photos") == []
        assert response.get_json().get("time_added") is not None


def test_get_product_by_id_fail_1(client, prepopulated_session):
    """Test getting product negative (product not found)"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")

    # When
    response = client.get("/products/product_info/1000000000")

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_product_by_id_success(client, prepopulated_session):
    """Test getting product success (product not found)"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")

    # When
    response = client.get("/products/product_info/1")

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get('id') is not None


def test_create_product_fail_1(client, prepopulated_session):
    """Test create new product negative (unauthorized user)"""
    # Given
    payload = {
        "category_id": 1,
        "sub_category_id": 11,
        "product_name": "new product",
        "price": 1500
    }

    # When
    response = client.post("/products/product", data=json.dumps(payload),
                           content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("payload", create_product_negative_payload)
def test_create_product_fail_2(payload, client, prepopulated_session):
    """Test create new product negative (fail validation)"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")

    # When
    response = client.post("/products/product", data=json.dumps(payload),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_product_fail_3(client, prepopulated_session):
    """Test create product fail (empty data)"""
    # Given
    authorize(client, email="1_test@mail.com", password="1_qwerty1S")
    payload = {}

    # When
    response = client.post("/products/product", data=json.dumps(payload))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.get_json().get("error") == "Empty request data"


def test_get_shop_products_success(client, prepopulated_session):
    """Test get shop products using prepopulated user data"""
    # Given
    expected_code = status.HTTP_200_OK
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")
    # When
    response = client.get("/products/shop_products", headers=headers)

    # Then
    assert response
    assert response.status_code == expected_code
    json_data = response.get_json()
    assert type(json_data) is dict
    assert len(json_data.get("data")) == 25


def test_create_product_success_2(client, session):
    """Test create product scenario success"""
    # Given
    create_user_and_shop(session)
    headers = authorize(client)

    # When
    response = client.post("/products/product", headers=headers,
                           json=TestValidData.get_product_payload(),
                           content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.get_json()
    assert json_data.get("message") == "Product created successfully"
    product: Product = Product.query.first()
    assert product.id > 0
    assert product.category_id == TestValidData.TEST_CATEGORY_ID
    assert product.is_active is True
    assert product.product_description == TestValidData.TEST_PRODUCT_DESCRIPTION
    assert product.product_name == TestValidData.TEST_PRODUCT_NAME
    assert product.shop_id > 0
    assert product.sub_category_name == TestValidData.TEST_SUB_CATEGORY_NAME
    assert product.time_added
    assert product.time_modifeid

    detail: ProductDetail = ProductDetail.query.first()
    assert detail.id > 0
    assert detail.product_id == product.id
    assert detail.price == TestValidData.TEST_PRODUCT_PRICE
    assert detail.product_status == TestValidData.TEST_PRODUCT_STATUS

    assert detail.is_unique is TestValidData.TEST_PRODUCT_IS_UNIQUE
    assert detail.is_return is TestValidData.TEST_PRODUCT_IS_RETURN

    assert detail.delivery_post == TestValidData.JSON_TEST_PRODUCT_DELIVERY_POST
    assert detail.product_characteristic == TestValidData.JSON_TEST_PRODUCT_CHARACTERISTIC
    assert detail.method_of_payment == TestValidData.JSON_TEST_PRODUCT_METHOD_OF_PAYMENT


def test_create_product_negative(client, session):
    """Test create shop product scenario negative: Shop not found"""
    # Given
    headers = authorize(client)

    response = client.post("/products/product", json=TestValidData.get_product_payload(),
                           content_type='application/json', headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.get_json().get("error") == "Shop not found"


@pytest.mark.parametrize('error_type, payload, expected_message', [
    ("wrong_category",
     {"category_id": 999},
     "The category with the specified ID does not exist"),
    ("wrong_category",
     {"sub_category_id": 999},
     "The subcategory with the specified ID does not belong to the category"),
    ("validation",
     {'product_status': '1',
      'product_name': 'ы',
      'product_description': 'ы',
      "product_characteristic": '_',
      "delivery_post": '_',
      "method_of_payment": '_'},
     None),
])
def test_create_product_negative_2(client, session, error_type, payload, expected_message):
    """Test create shop product scenario negative: wrong category_id, wrong subcategory_id
    and validation errors"""

    # Given
    headers = authorize(client)

    # When
    response = client.post("/products/product",
                           json=TestValidData.get_product_payload(**payload),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    if error_type == "validation":
        # Assert validation error for product status
        assert type(response.get_json().get("error")) == list
        keys = []  # noqa
        for key in response.get_json()["error"]:
            keys.append(key['loc'][0])
        assert 'product_status' in keys
        assert 'product_name' in keys
        assert 'product_description' in keys
        assert 'delivery_post' in keys
        assert 'product_characteristic' in keys
        assert 'method_of_payment' in keys

    else:
        assert response.get_json().get("error") == expected_message


def test_update_product_success(client, prepopulated_session):
    """Test update product using prepopulated user data"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")
    payload = {
        "product_name": "new name",
        "product_description": "new product description",
        "is_active": True,
        "price": 7000,
        "product_status": "Під замовлення"
    }

    # When
    with client:
        response = client.put("/products/update/1", data=json.dumps(payload),
                              content_type='application/json', headers=headers)

        # Then
        assert response
        assert response.status_code == status.HTTP_200_OK

        # After
        response = client.get(f"/products/product_info/1")
        assert response.status_code == status.HTTP_200_OK

        # Check each field of the product
        assert response.get_json().get("product_name") == payload["product_name"]
        assert response.get_json().get("product_description") == payload["product_description"]
        assert response.get_json().get("is_active") == payload["is_active"]
        assert response.get_json().get("price") == payload["price"]
        assert response.get_json().get("product_status") == payload["product_status"]


def test_update_product_fail_1(client, prepopulated_session):
    """Test update product negative (unauthorized user)"""
    # Given
    payload = {
        "product_name": "new name",
        "price": 1500
    }

    # When
    response = client.put("/products/update/1", data=json.dumps(payload),
                          content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("payload", create_product_negative_payload)
def test_update_product_fail_2(payload, client, prepopulated_session):
    """Test update product negative (fail validation)"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")

    # When
    response = client.post("/products/product", data=json.dumps(payload),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_add_product_photo_fail(client, prepopulated_session):
    """Test add photo to product fail scenario (product not exist)"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")

    # When
    with patch("werkzeug.datastructures.file_storage.FileStorage.save"):
        response = client.post('/products/product_photo/150000',
                               data={"image": TestValidData.get_image(), "main": True},
                               content_type='multipart/form-data', headers=headers)

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_product_fail_3(client, prepopulated_session):
    """Test update product fail (empty data)"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")
    payload = None

    # When
    response = client.post("/products/product", data=json.dumps(payload),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_add_product_photo_success(client, prepopulated_session):
    """Test add photo to product scenario success"""
    # Given
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")

    # When
    with patch("werkzeug.datastructures.file_storage.FileStorage.save"):
        response = client.post('/products/product_photo/1',
                               data={"image": TestValidData.get_image(),
                                     "main": True},
                               content_type='multipart/form-data', headers=headers)

        # Then
        assert response.status_code == status.HTTP_200_OK


def test_deactivate_product_success(client, prepopulated_session):
    """Test deactivate shop product and search products"""
    # Given
    expected_code = status.HTTP_200_OK
    expected_message = "Product deactivated"

    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")
    first = Product.query.first()

    # When
    response = client.delete(f"/products/deactivate/{first.id}", headers=headers)

    # Then
    assert response
    assert response.status_code == expected_code
    assert response.get_json().get("message") == expected_message
    assert first.is_active is False

    response = client.get("/products/shop_products", headers=headers)
    # Deactivated should be visible in view
    assert len(response.get_json().get("data")) == 25


@pytest.mark.parametrize("expected_code, expected_message",
                         ((404, "Shop not found"),
                          (404, "Shop not found")))
def test_deactivate_product_negative(client, session, expected_code, expected_message):
    """Test deactivate product scenario negative: Not found"""
    # Given
    if expected_code == 400:
        create_user_and_shop(session)
        headers = authorize(client)
    else:
        create_user_shop_product(session)
        headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")
    # When
    response = client.delete("/products/deactivate/1", headers=headers)

    assert response.status_code == expected_code
    assert response.get_json().get('error') == expected_message


@pytest.mark.parametrize("endpoint, method", (
        ("/products/deactivate/1", "delete"),
        ("/products/product", "post")
))
def test_unauthorized_endpoints(client, session, endpoint, method):
    """Test deactivate product scenario negative: Unauthorized"""
    # Given
    expected_code = 401
    expected_message = "Missing Authorization Header"

    # When
    if method == "post":
        response = client.post(endpoint)
    else:
        response = client.delete(endpoint)

    # Then
    assert response
    assert response.status_code == expected_code
    assert response.get_json().get("msg") == expected_message
