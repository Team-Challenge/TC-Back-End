import os.path
import io
import tempfile

import pytest
from flask import json, url_for
from werkzeug.datastructures import FileStorage

from models.products import Categories, Shop
from models.accounts import User
from tests import status
from tests.conftest import orint, authorize, get_payload, BASE_DIR
from models.shops import Shop

TEST_SHOP_DATA = {
    "owner_id": 1,
    "name": "ShopName Example. ІіЇїЄєЙйЄє",
    "description": "Example shop description. ІіЇїЄєЙйЄє",
    "phone_number": "+380123456789",
    "link": "https://example.com/",
    "banner_shop": None,
    "photo_shop": None
}


# def test_create_test_shop(session, photo_shop=False):
#     if photo_shop:
#         payload = TEST_SHOP_DATA.copy()
#         orint((io.BytesIO(b"abcdef"), 'test.jpg'))
#         # payload["photo_shop"] =
#         payload["photo_shop"] = "path/to/image.jpg"
#     else:
#         payload = TEST_SHOP_DATA
#     test_shop = Shop(**payload)
#     session.add(test_shop)
#     session.commit()
#     return test_shop


def test_create_shop(client, session):
    # To ensure than no shops are created before
    assert not session.query(Shop).first()
    headers, _valid_signup_data = authorize(client)
    valid_shop_payload = {
        "name": "ShopName Example. ІіЇїЄєЙйЄє",
        "description": "Example shop description. ІіЇїЄєЙйЄє",
        "phone_number": "+380123456789",
        "link": "https://example.com/"
    }
    response = client.post('/shops/shop', data=json.dumps(valid_shop_payload),
                           content_type='application/json', headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.get_json().get("message")

    shop = session.query(Shop).first()

    assert shop.name == valid_shop_payload["name"]
    assert shop.description == valid_shop_payload["description"]
    assert shop.phone_number == valid_shop_payload["phone_number"]
    assert shop.link == valid_shop_payload["link"]


def test_get_shop_info(client, session, create_test_shop):
    headers, _valid_signup_data = authorize(client)

    create_test_shop(session)
    response = client.get("/shops/shop_info", content_type='application/json', headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.get_json()
    assert data["description"] == TEST_SHOP_DATA["description"]
    assert data["link"] == TEST_SHOP_DATA["link"]
    assert data["name"] == TEST_SHOP_DATA["name"]
    assert data["phone_number"] == TEST_SHOP_DATA["phone_number"]


def test_post_shop_image(client, session, upload_image, create_test_shop):

    create_test_shop(session)
    headers, _valid_signup_data = authorize(client)
    with pytest.raises(TypeError):
        response = upload_image(headers, endpoint="/shops/shop_photo")
    session.commit()
    orint(session.query(Shop).first().__dict__)
    response = client.get("/shop/shop_photo", content_type='application/json', headers=headers)
    # fake_image = io.BytesIO(b'fake image data'), "file.jpg"
    # response = client.post("/shops/shop_photo", content_type='multipart/form-data',
    #                        data={"image": fake_image}, headers=headers)

    orint(response.__dict__)
    # response = client.get("/shops/shop_photo", content_type='application/json', headers=headers)
    # orint(response.__dict__)
    # assert response.status_code == status.HTTP_200_OK
