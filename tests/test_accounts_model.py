import pytest
from sqlalchemy.exc import IntegrityError
from unittest import mock
from models.accounts import User, Security
from tests.conftest import TestValidData as Data


def create_test_user(email=Data.TEST_EMAIL,
                     full_name=Data.TEST_FULL_NAME,
                     password=Data.TEST_PASSWORD):
    u = User.create_user(email, full_name, password)
    return u


def test_create_user_1(session):
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


def test_create_user_2(session):
    """Test create user scenario negative: Invalid email"""
    # Given
    email = None
    full_name = "TestName Full"
    password = "123467898qweW"

    # When
    with pytest.raises(IntegrityError):
        with mock.patch("models.accounts.Security.create_security", return_value=None) as f:
            u = User.create_user(email=email, full_name=full_name, password=password)

            # Then
            assert u.id is None
            assert u.email == email
            f.assert_not_called()


def test_get_user_by_id_1(session):
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


def test_get_user_by_id_2(session):
    """Test get user scenario negative"""
    # Given
    create_test_user()

    # When
    created: User = User.get_user_by_id(9999)

    # Then
    assert created is None


def test_change_number_1(session):
    pass
