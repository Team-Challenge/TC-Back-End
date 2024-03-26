from tests import status


def test_unauthorized_refresh_error(client):
    response = client.post("/accounts/refresh")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_change_phone_number_error(client):
    response = client.post("/accounts/change_phone_number")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_change_full_name_error(client):
    response = client.post("/accounts/change_full_name")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_delivery_info_error(client):
    response = client.post("/accounts/delivery_info")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_get_profile_photo_error(client):
    response = client.get("/accounts/profile_photo")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_profile_photo_error(client):
    response = client.post("/accounts/profile_photo")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_change_password_error(client):
    response = client.post("/accounts/change_password")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_info_error(client):
    response = client.get("/accounts/info")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_logout(client):
    response = client.delete("/accounts/logout")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
