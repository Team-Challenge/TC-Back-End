from unittest.mock import patch

import pytest
from flask import json

from tests import status
from tests.conftest import authorize, TestValidData

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


def test_create_product_success(client, prepopulated_session):
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
        assert response.get_json().get("product_characteristic") == payload["product_characteristic"]
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
    headers = authorize(client, email="1_test@mail.com", password="1_qwerty1S")
    payload = None

    # When
    response = client.post("/products/product", data=json.dumps(payload),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


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
        response = client.post('/products/product_photo/1', data={"image": TestValidData.get_image(),
                                                                  "main": True},
                               content_type='multipart/form-data', headers=headers)

        # Then
        assert response.status_code == status.HTTP_200_OK


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
