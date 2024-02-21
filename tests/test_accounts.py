from flask import json
from tests import status
from tests.conftest import orint, authorize, get_payload


def test_empty_email_signup_error(client, session):
    """The test returns an error if the email validation is successful"""
    valid_signup_data = {
        "email": "",
        "full_name": "Testname testlastname",
        "password": "Password1"
    }

    response = client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # If email errors exists in response
    json_data = response.get_json()
    assert json_data.get("email")


def test_invalid_password_signup_error(client, session):
    """The test returns an error if the password validation is successful"""
    valid_signup_data = {
        "email": "mail@example.com",
        "full_name": "Testname testlastname",
        "password": "Password"
    }

    response = client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # If password errors exists in response
    json_data = response.get_json()
    assert json_data.get("password")


def test_empty_password_signup_error(client, session):
    """The test returns an error if the password validation is successful"""
    valid_signup_data = {
        "email": "mail@example.com",
        "full_name": "Testname testlastname",
        "password": ""
    }

    response = client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # If password errors exists in response
    json_data = response.get_json()
    assert json_data.get("password")


def test_invalid_empty_full_name_signup_error(client, session):
    """Test returns error if validation for full name is success"""
    valid_signup_data = {
        "email": "mail@example.com",
        "full_name": "",
        "password": "Password1"
    }

    response = client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                           content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # If full_name error exists in response
    json_data = response.get_json()
    assert json_data.get("full_name")


def test_empty_payload_error(client, session):
    """Test returns error if validation for data is success"""
    valid_signup_data = {}

    response = client.post("/accounts/signup", data=json.dumps(valid_signup_data),
                           content_type="application/json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_signup_valid_response(client, session):
    """Test to ensure that server returns a proper response"""
    valid_signup_data = get_payload()

    response = client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                           content_type='application/json')
    assert response.status_code == status.HTTP_200_OK

    # If link, user(email, full_name, phone_number and profile_picture) exists in response
    data = response.get_json()
    assert data.get("link")
    assert data.get("user")
    assert data.get("user").get("email") == valid_signup_data.get("email")
    assert data.get("user").get("full_name") == valid_signup_data.get("full_name")

    # Endpoint returns phone_number and profile_picture as null
    assert data.get("user").get("phone_number") is None
    assert data.get("user").get("profile_picture") is None


def test_bad_token_error(client, session):
    """Test to authorize with bad token returns 404"""
    bad_token = "bad_token"
    response = client.get(f'/accounts/verify/{bad_token}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_data_success(client, session):
    """Test to ensure that user can change personal info"""
    headers, _valid_signup_data = authorize(client)

    # # # Change phone number
    valid_update_user_phone = {
        "phone_number": "+380972323233"
    }
    response = client.post('/accounts/change_phone_number', data=json.dumps(valid_update_user_phone),
                           content_type='application/json', headers=headers)
    assert response.status_code == status.HTTP_200_OK

    response = client.get("/accounts/profile_photo", content_type='application/json', headers=headers)


def test_update_user_full_name_success(client, session):
    """Test to ensure that user can change personal info"""

    # User creation and login
    headers, _valid_signup_data = authorize(client)

    # # # Change full_name
    valid_update_user_full_name = {
        "full_name": "Hello World ПривіІїЇт Світ жк-жк ABC-DEFґҐєЄ lk"
    }
    response = client.post('/accounts/change_full_name', data=json.dumps(valid_update_user_full_name),
                           content_type='application/json', headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_update_user_change_password_success(client, session):
    """Test to ensure that user can change personal info"""
    headers, valid_signup_data = authorize(client)

    # # # Change password
    valid_change_password_data = {
        "current_password": valid_signup_data.get("password"),
        "new_password": "sS123456789"
    }
    response = client.post('/accounts/change_password', data=json.dumps(valid_change_password_data),
                           content_type='application/json', headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_get_info_success(client, session):
    """Test to ensure that user can get info"""
    headers, _valid_signup_data = authorize(client)

    response = client.get("/accounts/info", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data: dict = response.get_json()
    assert data.get("address") is None
    assert data.get("branch_name") is None
    assert data.get("city") is None
    assert data.get("email")
    assert data.get("full_name")
    assert data.get("post") is None
    assert data.get("phone_number") is None
    assert data.get("profile_photo") is None
    assert data.get("post") is None


def test_logout_success(client, session):
    """Test to ensure that user can log out"""
    headers, _valid_signup_data = authorize(client)
    response = client.delete("/accounts/logout", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get("msg") == "Access token successfully revoked"


def test_token_refresh(client, session):
    """Test to ensure that user can receive access and refresh tokens"""
    headers, _valid_signup_data = authorize(client, refresh=True)
    response = client.post("/accounts/refresh", data=json.dumps({}),
                           content_type='application/json', headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get("access_token")
    assert response.get_json().get("refresh_token")


# # # Empty request tests
def test_empty_request_signup(client):
    """Test sending empty request returns unauthorized"""
    response = client.post("/accounts/signup", data=json.dumps({}))
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_empty_request_signin(client):
    """Test sending empty request returns unauthorized"""
    response = client.post("/accounts/signin", data=json.dumps({}))
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_empty_request_logout(client):
    """Test sending empty request returns unauthorized"""
    response = client.delete("/accounts/logout", data=json.dumps({}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_empty_request_change_phone_number(client):
    """Test sending empty request returns unauthorized"""
    response = client.post("/accounts/change_phone_number", data=json.dumps({}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_empty_requests_change_phone_number_authorized(client):
    """Test sending empty request when authorized"""
    response = client.post()



def test_empty_request_change_full_name(client):
    """Test sending empty request returns unauthorized"""
    response = client.post("/accounts/change_full_name", data=json.dumps({}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_empty_request_post_delivery_info(client):
    """Test sending empty request returns unauthorized"""
    response = client.post("/accounts/delivery_info", data=json.dumps({}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_empty_request_delete_delivery_info(client):
    """Test sending empty request returns unauthorized"""
    response = client.delete("/accounts/delivery_info", data=json.dumps({}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_empty_request_post_profile_photo(client):
    """Test sending empty request returns unauthorized"""
    response = client.post("/accounts/profile_photo", data=json.dumps({}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_empty_request_delete_profile_photo(client):
    """Test sending empty request returns unauthorized"""
    response = client.delete("/accounts/profile_photo", data=json.dumps({}))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

