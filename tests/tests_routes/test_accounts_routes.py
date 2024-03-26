from unittest.mock import patch

import pytest
from flask import json
from flask_jwt_extended import get_jwt_identity

from models.accounts import User
from tests import status

from tests.conftest import create_test_user, TestValidData, authorize, get_payload

signin_negative_payload = [
    {
        "email": "test1144@mail.com",
        "password": "A1234569654hfghg"
    },
    {
        "email": "test1144mail.com",
        "password": "123456"
    }
]

signup_negative_payload = [
    {
        "full_name": "Testname testlastname",
        "password": "Password1"
    },
    {
        "email": "mail@example.com",
        "password": "Password1"
    },
    {
        "email": "mail@example.com",
        "full_name": "Testname testlastname"
    },
    {
        "email": "mail@example.com",
        "full_name": "Testname testlastname  "
    },
    {
        "email": "mail@example.com",
        "full_name": "Testname  testlastname"
    },
    {
        "email": "mail@example.com",
        "full_name": " Testname testlastname"
    },
    {
        "email": "mail@example.com",
        "full_name": "Testname testlastnameы"
    },
]

change_phone_number_negative_payload = [
    {
        "phone_number": ""
    },
    {
        "phone_number": "0971122333"
    },
    {
        "phone_number": "380964455666"
    }
]

change_full_name_negative_payload = [
    {
        "full_name": " Testname testlastname"
    },
    {
        "full_name": "testname  testlastname"
    },
    {
        "full_name": "testname testlastname  "
    },
    {
        "full_name": "testname testlastnameы"
    },
    {
        "full_name": ""
    },
    {
        "full_name": "t"
    }
]

change_password_negative_payload = [
    {
        "current_password": TestValidData.TEST_PASSWORD,
        "password": ""
    },
    {
        "current_password": TestValidData.TEST_PASSWORD,
        "password": "pass"
    },
    {
        "password": "password"
    },
    {
        "current_password": TestValidData.TEST_PASSWORD,
        "password": "P assword"
    }
]


def test_signup_success(client, session):
    """The test returns successfully response"""
    # Given
    payload = {
        "email": "mail@example.com",
        "full_name": "Testname testlastname",
        "password": "Password1"
    }
    # When
    response = client.post('/accounts/signup', data=json.dumps(payload),
                           content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize("payload", signup_negative_payload)
def test_signup_fail(payload, client, session):
    """The test returns negative response"""
    # Given

    # When
    response = client.post('/accounts/signup', data=json.dumps(payload),
                           content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_signup_validation_fail(client, session):
    """The test returns negative response"""
    # Given
    payload = {
        "email": "mailexample.com",
        "full_name": "Test user ы",
        "password": "1234"
    }

    # When
    response = client.post('/accounts/signup', data=json.dumps(payload),
                           content_type='application/json')

    # Then
    json_data = response.get_json()['error']
    keys = []
    for key in json_data:
        keys.append(key['loc'][0])
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in keys
    assert 'password' in keys
    assert 'full_name' in keys


def test_signup_fail_1(client, session):
    """Test signup fail (empty data)"""
    # Given
    payload = None

    # When
    response = client.post("/accounts/signup", data=json.dumps(payload))

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_signin_success(client, session):
    """Successful response"""
    # Given
    create_test_user()
    payload = {
        "email": TestValidData.TEST_EMAIL,
        "password": TestValidData.TEST_PASSWORD
    }

    # When
    response = client.post('/accounts/signin', data=json.dumps(payload),
                           content_type='application/json')

    # Then
    json_data = response.get_json()
    assert response.status_code == status.HTTP_200_OK
    assert json_data.get('access_token') is not None
    assert json_data.get('refresh_token') is not None


def test_signin_fail_1(client, session):
    """Test signin fail (empty data)"""
    # Given
    payload = None

    # When
    response = client.post("/accounts/signin", data=json.dumps(payload))

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_signin_fail_2(client, session):
    """Negative response"""
    # Given
    payload = {
        "email": TestValidData.TEST_EMAIL,
        "password": TestValidData.TEST_PASSWORD
    }

    # When
    response = client.post('/accounts/signin', data=json.dumps(payload),
                           content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("payload", signin_negative_payload)
def test_signin_fail_3(payload, client, session):
    """Negative response"""
    # Given
    create_test_user()

    # When
    response = client.post('/accounts/signin', data=json.dumps(payload),
                           content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_unique_email_error(client, session):
    """Test to ensure that user cannot create multiple accounts using the same email"""
    # Given
    valid_signup_data = get_payload()

    # When
    response_1 = client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                             content_type='application/json')

    # Then
    assert response_1.status_code == status.HTTP_201_CREATED
    response_2 = client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                             content_type='application/json')
    assert response_2.status_code != status.HTTP_201_CREATED


def test_verification_email_successful(client, session):
    """Test email verification successful"""
    # Given
    valid_signup_data = {
        "email": "mail@example.com",
        "full_name": "Testname testlastname",
        "password": "Password1"
    }

    # When
    user = client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                       content_type='application/json')
    link = user.get_json()['link']
    response = client.get(link)

    # Then
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers['Location'] == "http://dorechi.store"


def test_verification_email_fail(client, session):
    """Test email verification fail"""
    # Given
    fail_token = "fail_token"

    # When
    response = client.get(f'/accounts/verify/{fail_token}')

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_refresh_token(client, session):
    """Test refresh token successful"""
    # Given
    headers = authorize(client, refresh=True)

    # When
    response = client.post("/accounts/refresh", data=json.dumps({}),
                           content_type='application/json', headers=headers)

    # Then
    data = response.get_json()
    assert response.status_code == 200
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_logout_successful(client, session):
    """Test logout successful"""
    # Given
    headers = authorize(client)

    # When
    response = client.delete("/accounts/logout", headers=headers)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get("msg") == "Access token successfully revoked"


def test_logout_fail(client, session):
    """Test logout fail (unauthorized)"""
    # When
    response = client.delete("/accounts/logout")

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_phone_number_successful(client, session):
    """Test change phone number successful"""
    # Given
    headers = authorize(client)
    phone = {
        "phone_number": "+380991122333"
    }

    # When
    response = client.post("/accounts/change_phone_number", data=json.dumps(phone),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get('message') == "OK"


def test_change_phone_number_fail_1(client, session):
    """Test change phone number fail (unauthorized)"""
    # When
    response = client.post("/accounts/change_phone_number")

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_phone_number_fail_2(client, session):
    """Test change phone number fail (empty data)"""
    # Given
    headers = authorize(client)
    phone = None

    # When
    response = client.post("/accounts/change_phone_number", data=json.dumps(phone),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("payload", change_phone_number_negative_payload)
def test_change_phone_number_fail_3(payload, client, session):
    """Negative response"""
    # Given
    headers = authorize(client)

    # When
    response = client.post('/accounts/change_phone_number', data=json.dumps(payload),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_change_full_name_successful(client, session):
    """Test change full name successful"""
    # Given
    headers = authorize(client)
    full_name = {
        "full_name": "Test full name new"
    }

    # When
    response = client.post("/accounts/change_full_name", data=json.dumps(full_name),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get('message') == "OK"


def test_change_full_name_fail_1(client, session):
    """Test change full name fail (unauthorized)"""
    # When
    response = client.post("/accounts/change_full_name")

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_full_name_fail_2(client, session):
    """Test change full name fail (empty data)"""
    # Given
    headers = authorize(client)
    full_name = None

    # When
    response = client.post("/accounts/change_full_name", data=json.dumps(full_name),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("payload", change_full_name_negative_payload)
def test_change_full_name_fail_3(payload, client, session):
    """Negative response change full name"""
    # Given
    headers = authorize(client)

    # When
    response = client.post('/accounts/change_full_name', data=json.dumps(payload),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_info_success(client, session):
    """Test to ensure that user can get info"""
    # Given
    headers = authorize(client)

    # When
    response = client.get("/accounts/info", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    # Then
    data: dict = response.get_json()
    assert data.get("address") is None
    assert data.get("branch_name") is None
    assert data.get("city") is None
    assert data.get("email")
    assert data.get("full_name")
    assert data.get("post") is None
    assert data.get("phone_number") is None
    assert data.get("profile_photo") is None


def test_change_password_successful(client, session):
    """Test change password successful"""
    # Given
    headers = authorize(client)
    password = {
        "current_password": "123467898qweW",
        "new_password": "neWpassword1"
    }

    # When
    response = client.post("/accounts/change_password", data=json.dumps(password),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get('message') == "OK"


def test_change_password_fail_1(client, session):
    """Test change password fail (unauthorized)"""
    # When
    response = client.post("/accounts/change_password")

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_password_fail_2(client, session):
    """Test change password fail (empty data)"""
    # Given
    headers = authorize(client)
    password = None

    # When
    response = client.post("/accounts/change_password", data=json.dumps(password),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("payload", change_password_negative_payload)
def test_change_password_fail_3(payload, client, session):
    """Negative response change_password"""
    # Given
    headers = authorize(client)

    # When
    response = client.post('/accounts/change_password', data=json.dumps(payload),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_manage_delivery_info_success(client, session):
    """Test manage delivery info success"""
    # Given
    headers = authorize(client)
    delivery_request = {
        "post": "nova_post",
        "city": "Kiev",
        "branch_name": "19",
        "address": "Eschatology, 21"
    }
    # When
    response = client.post("/accounts/delivery_info", data=json.dumps(delivery_request),
                           content_type='application/json', headers=headers)

    # Before then
    assert response.status_code == status.HTTP_200_OK
    user = client.get("/accounts/info", headers=headers)
    data: dict = user.get_json()
    assert data.get("address") == delivery_request['address']
    assert data.get("branch_name") == delivery_request['branch_name']
    assert data.get("city") == delivery_request['city']
    assert data.get("post") == delivery_request['post']

    # After then
    response = client.delete("/accounts/delivery_info", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    user = client.get("/accounts/info", headers=headers)
    data: dict = user.get_json()
    assert data.get("address") is None
    assert data.get("branch_name") is None
    assert data.get("city") is None
    assert data.get("post") is None


def test_manage_delivery_info_fail_1(client, session):
    """Test manage delivery info fail (unauthorized)"""
    # When
    response = client.post("/accounts/delivery_info")

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_manage_delivery_info_fail_2(client, session):
    """Test change password fail (empty data)"""
    # Given
    headers = authorize(client)
    delivery_request = None

    # When
    response = client.post("/accounts/delivery_info", data=json.dumps(delivery_request),
                           content_type='application/json', headers=headers)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_upload_profile_photo_success(client, session):
    """Test upload image profile scenario success"""
    # Given
    headers = authorize(client)

    # When
    with patch("werkzeug.datastructures.file_storage.FileStorage.save"):
        response = client.post('/accounts/profile_photo', data={"image": TestValidData.get_image()},
                               content_type='multipart/form-data', headers=headers)

        # Then post
        assert response.status_code == status.HTTP_200_OK
        user_id = get_jwt_identity()
        user_data = User.get_user_by_id(user_id)
        assert user_data.profile_picture is not None

        # Then delete
        response = client.delete('/accounts/profile_photo', headers=headers)

        assert response.status_code == status.HTTP_200_OK
        user_data = User.get_user_by_id(user_id)
        assert user_data.profile_picture is None
