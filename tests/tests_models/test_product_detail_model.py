import pytest

from models.errors import NotFoundError
from models.products import ProductDetail
from tests.conftest import TestValidData as Data
from tests.conftest import create_user_shop_product


def test_create_product_detail_1(session):
    """Test create product detail scenario success"""
    # Given
    user, shop, product, detail = create_user_shop_product(session)
    # When
    response = ProductDetail.add_product_detail(**Data.get_product_detail_payload(product.id))

    # Then
    assert response
    assert response.id
    assert response.price == Data.TEST_PRODUCT_PRICE
    assert response.product_status is None
    assert response.product_characteristic == Data.JSON_TEST_PRODUCT_CHARACTERISTIC
    assert response.delivery_post == Data.JSON_TEST_PRODUCT_DELIVERY_POST
    assert response.method_of_payment == Data.JSON_TEST_PRODUCT_METHOD_OF_PAYMENT


# def test_create_product_detail_2(session):
#     """Test create product detail scenario negative: Not found"""
#     # Given
#     user, shop, product = create_user_shop_product(session)
#     invalid_product_id = 9999
#
#     # When
#     response = ProductDetail.add_product_detail(invalid_product_id, **Data.get_product_detail_payload(product.id))

def test_get_product_detail_success(session):
    """Test get product detail scenario success"""
    # Given
    user, shop, product, detail = create_user_shop_product(session)
    result: ProductDetail = ProductDetail.get_product_detail_by_product_id(product.id)
    assert result
    for r, d in zip(result.__dict__, detail.__dict__):
        assert r == d


def test_get_product_detail_negative(session):
    """Test get product detail scenario negative: Not found"""
    # Given
    invalid_product_id = 9999
    result = ProductDetail.get_product_detail_by_product_id(invalid_product_id)
    assert result is None


def test_update_product_detail_success(session):
    """Test update product detail scenario success"""
    # Given
    user, shop, product, detail = create_user_shop_product(session)
    new_payload = {
        "product_id": product.id,
        "price": 9999.25,
        "product_characteristic": "Color: Red",
        "delivery_post": "ukr_post",
        "method_of_payment": "mental"
    }

    # When
    result = ProductDetail.update_product_detail(**new_payload)

    # Then
    assert result
    assert result.get("message")
    edited = ProductDetail.query.filter_by(**new_payload).first()
    assert edited.price == new_payload["price"]
    assert edited.product_characteristic == new_payload["product_characteristic"]
    assert edited.delivery_post == new_payload["delivery_post"]
    assert edited.method_of_payment == new_payload["method_of_payment"]


def test_update_product_detail_negative(session):
    """Test update product detail scenario negative: Product detail not found"""
    # Given
    invalid_product_id = 9999
    new_payload = {
        "product_id": invalid_product_id,
        "price": 9999.25,
        "product_characteristic": "Color: Red",
        "delivery_post": "ukr_post",
        "method_of_payment": "mental"
    }

    # When
    with pytest.raises(NotFoundError, match="Product detail not found"):
        result = ProductDetail.update_product_detail(**new_payload)
    # Then
    with pytest.raises(UnboundLocalError):
        assert result
