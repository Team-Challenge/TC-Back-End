import json
from unittest.mock import patch

import pytest

from models.shops import Shop
from tests import status
from tests.conftest import (authorize, TestValidData, create_user_shop_product,
                            create_user_and_shop, create_test_user)

shop_routes = (
    {"route": "/shops/shop", "method": "POST"},
    {"route": "/shops/shop_photo", "method": "POST"},
    {"route": "/shops/shop_photo", "method": "DELETE"},
    {"route": "/shops/shop_banner", "method": "POST"},
    {"route": "/shops/shop_banner", "method": "DELETE"},
    {"route": "/products/shop_products", "method": "GET"},
    {"route": "/shops/shop_info", "method": "GET"},
)
post_routes = (route for route in shop_routes if route["method"] == "POST")
bad_shop_payloads = (
    {"name": "",
     "description": "",
     "phone_number": "",
     "link": ""},
    {"name": "ы",
     "description": "ы",
     "phone_number": "ы",
     "link": ""}
)


def test_create_shop_success(client, session):
    """Test create shop scenario success"""
    # Given
    user = create_test_user()
    headers = authorize(client)

    # When
    response = client.post('/shops/shop', data=json.dumps(TestValidData.get_shop_payload()),
                           headers=headers, content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_201_CREATED
    assert response.get_json().get("message") == "Shop created successfully"

    found: Shop = Shop.query.filter_by(owner_id=user.id).first()
    assert found
    assert found.name == TestValidData.TEST_SHOP_NAME
    assert found.description == TestValidData.TEST_SHOP_DESCRIPTION
    assert found.phone_number == TestValidData.TEST_SHOP_PHONE_NUMBER
    assert found.link == TestValidData.TEST_SHOP_LINK


@pytest.mark.parametrize("method", ("create", "update"))
@pytest.mark.parametrize("payload", bad_shop_payloads)
def test_create_update_shop_negative(client, session, payload, method):
    """Test create and update shop scenario negative: Validation errors"""
    # Given
    if method == "create":
        create_user_shop_product(session)
    headers = authorize(client)

    # When
    response = client.post('/shops/shop', data=json.dumps(payload),
                           headers=headers, content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_data = response.get_json()["error"]
    keys = []  # noqa
    for key in json_data:
        keys.append(key['loc'][0])
    assert 'name' in keys
    assert 'description' in keys
    assert 'phone_number' in keys
    assert 'link' not in keys


def test_update_shop_success(client, session):
    """Test update shop scenario success"""
    # Given
    data = create_user_shop_product(session)
    headers = authorize(client)
    new_payload = {
        "name": "New Test Name",
        "description": "New Test Description",
        "phone_number": "+380111111141",
        "link": "NewTestLink",
    }

    # When
    response = client.post('/shops/shop', data=json.dumps(new_payload),
                           headers=headers, content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get("message") == "Shop updated successfully"

    found: Shop = Shop.query.filter_by(owner_id=data.user.id).first()
    assert found.id == data.shop.id
    assert found.name == new_payload["name"]
    assert found.description == new_payload["description"]
    assert found.phone_number == new_payload["phone_number"]
    assert found.link == new_payload["link"]


def test_upload_shop_photo_success(client, session):
    """Test upload image for shop scenario success"""
    # Given
    data = create_user_shop_product(session)
    headers = authorize(client)

    # When
    with patch("werkzeug.datastructures.file_storage.FileStorage.save"):
        response = client.post('/shops/shop_photo', data={"image": TestValidData.get_image()},
                               content_type='multipart/form-data', headers=headers)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.get_json()["photo_shop"]
        found = Shop.query.filter_by(id=data.shop.id).first()
        assert found.photo_shop
        assert found.photo_shop in response.get_json()["photo_shop"]


def test_delete_shop_photo_success(client, session):
    """Test delete image from shop scenario success"""
    # Given
    data = create_user_shop_product(session)
    data.shop.photo_shop = "sample_name.jpg"
    session.add(data.shop)
    session.commit()
    headers = authorize(client)

    # When
    found = Shop.query.filter_by(id=data.shop.id).first()
    response = client.delete('/shops/shop_photo', headers=headers)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert found.photo_shop is None


@pytest.mark.parametrize("endpoint, to_check",
                         (("/shops/shop_photo", "photo_shop"),
                          ("/shops/shop_banner", "shop_banner")))
def test_get_shop_photo_banner_success(client, session, endpoint, to_check):
    """Test get photo and banner from shop scenario success"""
    # Given
    data = create_user_shop_product(session)
    filename = "sample_name.jpg"
    if to_check == "photo_shop":
        data.shop.photo_shop = filename
    else:
        data.shop.banner_shop = filename
    session.commit()
    headers = authorize(client)

    # When
    response = client.get(endpoint, headers=headers)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get(to_check)
    assert filename in response.get_json().get(to_check)


def test_upload_shop_banner_success(client, session):
    """Test upload banner to shop scenario success"""
    # Given
    data = create_user_shop_product(session)
    headers = authorize(client)

    # When
    with patch("werkzeug.datastructures.file_storage.FileStorage.save"):
        response = client.post('/shops/shop_banner', data={"image": TestValidData.get_image()},
                               content_type='multipart/form-data', headers=headers)

        # Then
        assert response.status_code == status.HTTP_200_OK

    assert response.get_json()["shop_banner"]
    found = Shop.query.filter_by(id=data.shop.id).first()
    assert found.banner_shop
    assert found.banner_shop in response.get_json()["shop_banner"]


def test_delete_shop_banner_success(client, session):
    """Test delete banner from shop scenario success"""
    # Given
    data = create_user_shop_product(session)
    headers = authorize(client)
    filename = "sample_name.jpg"
    data.shop.banner_shop = filename
    session.commit()

    # When
    response = client.delete('/shops/shop_banner', data={"image": TestValidData.get_image()},
                             content_type='multipart/form-data', headers=headers)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json()["message"] == "OK"
    found = Shop.query.filter_by(id=data.shop.id).first()
    assert found.banner_shop is None


@pytest.mark.parametrize("endpoint, expected_response",
                         (("/shops/shop_photo", "Photo shop not found"),
                          ("/shops/shop_banner", "Banner shop not found"),
                          ("/shops/shop_photo", "Shop not found"),
                          ("/shops/shop_banner", "Shop not found")))
def test_get_shop_images_negative(client, session, endpoint, expected_response):
    """Test get images from shop scenario negative: Not found"""
    # Given
    if expected_response != "Shop not found":
        create_user_shop_product(session)
    headers = authorize(client)

    # When
    response = client.get(endpoint, headers=headers)

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.get_json()["error"] == expected_response


def test_get_shop_info_success(client, session):
    """Test get shop info scenario success"""
    # Given
    create_user_shop_product(session)
    headers = authorize(client)

    # When
    response = client.get('/shops/shop_info', headers=headers)

    # Then
    assert response.status_code == status.HTTP_200_OK

    json_data = response.get_json()
    assert json_data.get("id")
    assert json_data.get("owner_id")
    assert json_data.get("name")
    assert json_data.get("description")
    assert json_data.get("photo_shop", "wrong") is None
    assert json_data.get("banner_shop", "wrong") is None
    assert json_data.get("phone_number")
    assert json_data.get("link")


def test_get_shop_info_negative(client, session):
    """Test get shop info scenario negative: Shop not found"""
    # Given
    headers = authorize(client)

    # When
    response = client.get('/shops/shop_info', headers=headers)

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND
    json_data = response.get_json()
    assert json_data.get("error") == "Shop not found"


@pytest.mark.parametrize("routes", shop_routes)
def test_shop_routes_unauthorized_negative(client, session, routes):
    """Test routes for unauthorized access scenario negative: Unauthorized"""
    # Given
    # When
    if routes["method"] == "POST":
        response = client.post(routes["route"])
    elif routes["method"] == "DELETE":
        response = client.delete(routes["route"])
    elif routes["method"] == "GET":
        response = client.get(routes["route"])

    # Then
    assert response  # noqa
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.get_json().get('msg') == "Missing Authorization Header"


@pytest.mark.parametrize("routes", post_routes)
def test_shop_routes_empty_request_negative(client, session, routes):
    """Test routes for unauthorized access scenario negative: Empty request"""
    # Given
    create_user_and_shop(session)
    headers = authorize(client)

    # When
    response = client.post(routes["route"], data=json.dumps({}), headers=headers,
                           content_type='application/json')
    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.get_json().get("error") == "Invalid request data"
