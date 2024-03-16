from datetime import datetime
from unittest import mock

import pytest
from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature
from sqlalchemy.exc import IntegrityError

from models.accounts import User, Security
from models.errors import UserError, NotFoundError
from tests.conftest import TestValidData as Data, open_mock, create_test_user


# todo sign_in
# todo change_number
# todo change_full_name
# todo get_user_info
# todo handle_profile_photo
# todo change_password
# todo verify_email


def create_mock_users():
    users = []
    with open_mock("valid_users.csv") as data:
        for row in data:
            users.append(create_test_user(**row))
    return users


def test_create_user_1(prepopulated_session):
    """Test create user scenario success"""
    # Given
    email = "test@mail.com"
    full_name = "TestName Full"
    password = "123467898qweW"

    # When
    u = User.create_user(email=email, full_name=full_name, password=password)
    s = Security.get_user_password_hash(u.id)

    # Then
    assert u.id > 0
    assert u.email == email
    assert s is not None
    assert s != password


def test_create_user_2(prepopulated_session):
    """Test create user scenario negative: Invalid email"""
    # Given
    email = None
    full_name = "TestName Full"
    password = "123467898qweW"

    # When
    with pytest.raises(IntegrityError):
        with mock.patch("models.accounts.Security.create_security", return_value=None) as f:
            u = User.create_user(email=email, full_name=full_name, password=password)  # noqa

            # Then
            assert u.id is None
            assert u.email == email
            f.assert_not_called()


def test_create_user_3(session):
    """Test to create multiple users with the same email
    using mock data scenario negative"""
    # Given
    with open_mock("invalid_users.csv") as data:
        users = []

        # When
        with pytest.raises(IntegrityError):
            for row in data:
                users.append(create_test_user(**row))  # noqa

    # Then
    assert len(users) == 1


def test_get_user_by_id_1(prepopulated_session):
    """Test get user scenario success"""
    # Given
    u = create_test_user()

    # When
    created: User = User.get_user_by_id(u.id)

    # Then
    assert created
    assert created.id > 0
    assert created.email
    assert created.full_name


def test_get_user_by_id_2(prepopulated_session):
    """Test get user scenario negative: User is not found"""
    # Given
    create_test_user()

    # When
    created: User = User.get_user_by_id(9999)

    # Then
    assert created is None


def test_sign_in_1(prepopulated_session):
    # Given
    create_test_user()

    # When
    tokens = User.sign_in(Data.TEST_EMAIL, Data.TEST_PASSWORD)

    # Then
    assert tokens.get("access_token")
    assert tokens.get("refresh_token")


def test_sign_in_2(prepopulated_session):
    """Test sign in scenario negative: User not found"""
    # Given
    create_test_user()

    # When
    with pytest.raises(UserError, match="User not found"):
        tokens = User.sign_in("wrong@mail.com", Data.TEST_PASSWORD)

    # Then
    with pytest.raises(UnboundLocalError):
        assert tokens


def test_sign_in_3(prepopulated_session):
    """Test sign in scenario negative: Wrong password"""
    # Given
    create_test_user()

    # When
    with pytest.raises(UserError, match="Incorrect password"):
        tokens = User.sign_in(Data.TEST_EMAIL, "qwerty")

    # Then
    with pytest.raises(UnboundLocalError):
        assert tokens


def test_change_number_1(prepopulated_session):
    """Test change number scenario success"""
    # Given
    u = create_test_user()
    phone_number = "+380999999999"

    # When
    result = User.change_number(u.id, phone_number=phone_number)

    # Then
    assert result
    assert result.get("message")
    assert User.get_user_by_id(u.id).phone_number == phone_number


def test_change_number_2(session):
    """Test change number scenario negative: User not found"""
    # Given
    phone_number = "1234567890"

    # When
    with pytest.raises(NotFoundError, match="User not found"):
        result = User.change_number(9999, phone_number)

    # Then
    with pytest.raises(UnboundLocalError):
        assert result


def test_change_full_name_1(prepopulated_session):
    """Test change full name scenario success"""
    # Given
    u = create_test_user()
    full_name = "New FullName"
    # When
    result = User.change_full_name(u.id, full_name)

    # Then
    assert result
    assert result.get("message")
    assert User.get_user_by_id(u.id).full_name == full_name


def test_change_full_name_2(prepopulated_session):
    """Test change full name scenario negative: User not found"""
    # Given
    full_name = "New FullName"
    # When
    with pytest.raises(NotFoundError, match="User not found"):
        result = User.change_full_name(9999, full_name)

    # Then
    with pytest.raises(UnboundLocalError):
        assert result


def test_get_user_info_1(session):
    """Test return user info scenario success"""
    # Given
    u = create_test_user()

    # When
    result = User.get_user_info(u.id)

    # Then
    assert result
    assert result.get("id")
    assert result.get("email") == Data.TEST_EMAIL
    assert result.get("full_name") == Data.TEST_FULL_NAME
    assert result.get("profile_picture") is None
    assert type(result.get("joined_at")) is datetime
    assert result.get("phone_number") is None
    assert result.get("is_active") is False


def test_get_user_info_2(prepopulated_session):
    """Test return user info scenario negative: User not found"""
    # Given
    wrong_user_id = 9999

    # When
    with pytest.raises(NotFoundError, match="User not found"):
        result = User.get_user_info(wrong_user_id)

    # Then
    with pytest.raises(UnboundLocalError):
        assert result


def test_change_password_1(prepopulated_session):
    """Test change password scenario success"""
    # Given
    u = create_test_user()
    old_pass_hash = Security.get_user_password_hash(u.id)
    new_password = "qwerty123Q"

    # When
    result = User.change_password(u.id,
                                  current_password=Data.TEST_PASSWORD,
                                  new_password=new_password)
    # Then
    assert result
    assert result.get("message")
    new_password_hash = Security.get_user_password_hash(u.id)
    assert old_pass_hash != new_password_hash


def test_change_password_2(prepopulated_session):
    """Test change password scenario negative: User not found"""
    # Given
    wrong_user_id = 9999
    new_password = "qwerty123Q"

    # When
    with pytest.raises(NotFoundError, match="User not found"):
        result = User.change_password(user_id=wrong_user_id,
                                      current_password=Data.TEST_PASSWORD,
                                      new_password=new_password)

    # Then
    with pytest.raises(UnboundLocalError):
        assert result


def test_verify_email_1(prepopulated_session):
    """Test verify email scenario success"""
    # Given
    create_test_user()
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(Data.TEST_EMAIL, salt='email-verification')

    # When
    result = User.verify_email(token, serializer)

    # Then
    assert result == "OK"


def test_verify_email_2(session):
    """Test verify multiple emails scenario success"""
    # Given
    users = create_mock_users()
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    # When
    for user in users:
        token = serializer.dumps(user.email, salt='email-verification')
        result = User.verify_email(token, serializer)

        # Then
        assert result == "OK"


def test_verify_email_3(session):
    """Test verify email scenario negative: Bad Signature"""
    # Given
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(Data.TEST_EMAIL, salt='email-verification')
    token += "s"

    # When
    with pytest.raises(BadSignature):
        result = User.verify_email(token, serializer)

    # Then
    with pytest.raises(UnboundLocalError):
        assert result
