import pytest

from models.errors import NotFoundError, UserError
from models.products import Product, get_all_shop_products
from tests.conftest import (create_test_user, create_user_and_shop, create_user_shop_product,
                            TestValidData)


def test_create_product_1(session):
    """Test create product scenario success"""
    # Given
    user, shop = create_user_and_shop(session)

    # When
    response = Product.add_product(user_id=user.id,
                                   **TestValidData.get_product_payload(is_json=True))

    # Then
    assert response

    product = Product.query.filter_by(shop_id=shop.id,
                                      category_id=TestValidData.TEST_CATEGORY_ID,
                                      product_name=TestValidData.TEST_PRODUCT_NAME,
                                      product_description=TestValidData.TEST_PRODUCT_DESCRIPTION).first()
    assert product.id > 0
    assert product.shop_id == shop.id
    assert product.category_id == TestValidData.TEST_CATEGORY_ID
    assert product.sub_category_name == TestValidData.TEST_SUB_CATEGORY_NAME
    assert product.product_name == TestValidData.TEST_PRODUCT_NAME
    assert product.product_description == TestValidData.TEST_PRODUCT_DESCRIPTION
    assert product.product_to_detail


def test_create_product_2(session):
    """Test create product scenario negative: Shop not found"""
    # Given
    user = create_test_user()

    # When
    with pytest.raises(NotFoundError, match="Shop not found"):
        response = Product.add_product(user_id=user.id, **TestValidData.get_product_payload())

    # Then
    with pytest.raises(UnboundLocalError):
        assert response


def test_create_product_3(session):
    """Test create product scenario negative: User not found"""
    # Given
    create_user_and_shop(session)
    invalid_user_id = 999
    # When
    with pytest.raises(UserError, match="User not found"):
        response = Product.add_product(user_id=invalid_user_id,
                                       **TestValidData.get_product_payload())

    # Then
    with pytest.raises(UnboundLocalError):
        assert response


def test_delete_product_1(session):
    """Test delete product scenario success"""
    # Given
    user, _shop, product, detail = create_user_shop_product(session)

    # When
    response = Product.delete_product(user_id=user.id, product_id=product.id)

    # Then
    assert response
    assert response.get("message") == "Ok"

    product = Product.query.filter_by(id=product.id).first()
    assert not product.is_active


def test_delete_product_2(session):
    """Test delete product scenario negative: Product not found"""
    # Given
    user, _shop = create_user_and_shop(session)
    invalid_product_id = 9999

    # When
    with pytest.raises(UserError, match="Product not found or permission not granted"):
        response = Product.delete_product(user_id=user.id, product_id=invalid_product_id)

    # Then
    with pytest.raises(UnboundLocalError):
        assert response


def test_delete_product_3(session):
    """Test delete product scenario negative: User is not owner / Has no permission"""
    # Given
    user, _shop, product, detail = create_user_shop_product(session)
    invalid_user, _shop = create_user_and_shop(session, email="invalid@user.com")

    # When
    with pytest.raises(UserError, match="Product not found or permission not granted"):
        response = Product.delete_product(user_id=invalid_user.id, product_id=product.id)

    # Then
    with pytest.raises(UnboundLocalError):
        assert response


def test_delete_product_4(session):
    """Test delete product scenario negative: User not found"""
    # Given
    user, _shop, product, detail = create_user_shop_product(session)
    invalid_user_id = 9999

    # When
    with pytest.raises(NotFoundError, match="User not found"):
        response = Product.delete_product(user_id=invalid_user_id, product_id=product.id)

    # Then
    with pytest.raises(UnboundLocalError):
        assert response


def test_delete_product_5(session):
    """Test delete product scenario negative: Shop not found"""
    # Given
    user = create_test_user()
    invalid_product_id = 9999

    # When
    with pytest.raises(NotFoundError, match="Shop not found"):
        response = Product.delete_product(user_id=user.id, product_id=invalid_product_id)

    # Then
    with pytest.raises(UnboundLocalError):
        assert response


def test_get_product_by_id_1(session):
    """Test delete product scenario success"""
    # Given
    user, shop, created_product, detail = create_user_shop_product(session)

    # When
    found_product: Product = Product.get_product_by_id(product_id=created_product.id)
    # Then
    assert found_product
    assert found_product.id == created_product.id
    assert found_product.category_id == created_product.category_id
    assert found_product.sub_category_name == created_product.sub_category_name
    assert found_product.shop_id == created_product.shop_id
    assert found_product.product_name == created_product.product_name
    assert found_product.product_description == created_product.product_description
    assert found_product.time_added == created_product.time_added
    assert found_product.time_modifeid == created_product.time_modifeid
    assert found_product.category == created_product.category
    assert found_product.product_to_comment == created_product.product_to_comment


def test_get_product_by_id_2(session):
    """Test delete product scenario negative: Not found"""
    # Given
    invalid_product_id = 9999

    # When
    product = Product.get_product_by_id(invalid_product_id)

    # Then
    assert product is None


def test_update_product_1(session):
    """Test update product scenario success"""
    # Given
    user, shop, product, detail = create_user_shop_product(session)
    new_payload = {"product_id": product.id,
                   "category_id": 9999,
                   "sub_category_name": "Wrong subcat",
                   "shop_id": shop.id,
                   "product_name": "New Product Name",
                   "product_description": "New Description",
                   "is_active": False}

    # When
    response = Product.update_product(user_id=user.id, **new_payload)
    # Then
    assert response
    assert response.get("message")

    edited = Product.query.filter_by(id=product.id).first()
    assert edited.shop_id == new_payload["shop_id"]
    assert edited.product_name == new_payload["product_name"]
    assert edited.product_description == new_payload["product_description"]
    assert edited.is_active == new_payload["is_active"]
    # Category and SubCategory should not be changed
    assert edited.category_id == product.category_id
    assert edited.sub_category_name == product.sub_category_name


def test_update_product_2(session):
    """Test update product scenario negative: Product not found or not belong to shop"""
    # Given
    user, shop, product, detail = create_user_shop_product(session)
    invalid_user, _shop = create_user_and_shop(session, email="invalid@user.com")

    # When
    new_payload = {"product_id": product.id,
                   "shop_id": shop.id,
                   "product_name": "New Product Name",
                   "product_description": "New Description",
                   "is_active": False}

    # When
    with pytest.raises(UserError, match="Product not found or not belong to shop"):
        Product.update_product(user_id=invalid_user.id, **new_payload)

    # Then
    not_edited = Product.query.filter_by(id=product.id).first()
    assert not_edited.shop_id == product.shop_id
    assert not_edited.product_name == product.product_name
    assert not_edited.product_description == product.product_description
    assert not_edited.is_active == product.is_active


def test_update_product_3(session):
    """Test update product scenario negative: Shop or product not found: Product not found"""
    # Given
    user, shop, product, detail = create_user_shop_product(session)
    invalid_product_id = 9999
    new_payload = {"product_id": invalid_product_id,
                   "shop_id": shop.id,
                   "product_name": "New Product Name",
                   "product_description": "New Description",
                   "is_active": False}

    # When
    with pytest.raises(NotFoundError, match="Shop or product not found"):
        Product.update_product(user_id=user.id, **new_payload)

    # Then
    not_edited = Product.query.filter_by(id=product.id).first()
    assert not_edited.shop_id == product.shop_id
    assert not_edited.product_name == product.product_name
    assert not_edited.product_description == product.product_description
    assert not_edited.is_active == product.is_active


def test_update_product_4(session):
    """Test update product scenario negative: User not found"""
    # Given
    user, shop, product, detail = create_user_shop_product(session)
    invalid_user_id = 9999
    new_payload = {"product_id": product.id,
                   "shop_id": shop.id,
                   "product_name": "New Product Name",
                   "product_description": "New Description",
                   "is_active": False}

    # When
    with pytest.raises(NotFoundError, match="User not found"):
        Product.update_product(user_id=invalid_user_id, **new_payload)

    # Then
    not_edited = Product.query.filter_by(id=product.id).first()
    assert not_edited.shop_id == product.shop_id
    assert not_edited.product_name == product.product_name
    assert not_edited.product_description == product.product_description
    assert not_edited.is_active == product.is_active


def test_get_all_shop_products_1(session):
    """Test to get all shop products scenario negative: No photo and detail"""
    # Given
    user, shop = create_user_and_shop(session)
    products = []
    for i in range(0, 15):
        products.append(Product(shop_id=shop.id, **TestValidData.get_product_payload()))
    session.add_all(products)
    session.commit()
    # When

    result = get_all_shop_products(user.id)

    # Then
    assert len(Product.query.filter_by(shop_id=shop.id).all()) == 15
    assert len(result) == 0


def test_get_all_shop_products_2(session):
    """Test to get all shop products scenario negative: Shop not found"""
    # Given
    user = create_test_user()

    # When
    with pytest.raises(NotFoundError, match="Shop not found"):
        get_all_shop_products(user.id)


def test_get_all_shop_products_3(session):
    """Test to get all shop products scenario negative: User not found"""
    # Given
    invalid_user_id = 9999

    # When
    with pytest.raises(NotFoundError, match="User not found"):
        get_all_shop_products(invalid_user_id)
