import pytest

from models.products import Product, ProductDetail
from tests import status
from tests.conftest import (authorize, create_user_and_shop, TestValidData,
                            create_user_shop_product)


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
    assert type(response.get_json()) == list
    assert len(response.get_json()) == 25


def test_create_product_success(client, session):
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
    assert json_data.get("message") == "The product was created successfully"
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
    assert len(response.get_json()) == 25


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
