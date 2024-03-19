import pytest
from flask import json
from tests import status

from tests.conftest import create_test_user, TestValidData

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


def test_signin_success(client, session):
    """Succeful response"""
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
def test_signin_fail_2(payload, client, session):
    """Negative response"""
    # Given
    create_test_user()

    # When
    response = client.post('/accounts/signin', data=json.dumps(payload),
                           content_type='application/json')

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
