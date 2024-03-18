import pytest

from models.accounts import User, Security
from models.errors import UserError, NotFoundError
from tests.conftest import TestValidData as Data, create_test_user


def test_create_security_1(prepopulated_session):
    """Test create security scenario success"""
    # Given
    u = User(email=Data.TEST_EMAIL, full_name=Data.TEST_FULL_NAME)
    prepopulated_session.add(u)
    prepopulated_session.commit()

    # Then
    security = Security.create_security(user_id=u.id,
                                        password=Data.TEST_PASSWORD)

    # When
    assert security
    assert security != Data.TEST_PASSWORD


def test_security_change_password_1(prepopulated_session):
    """Test change user security password scenario success"""
    # Given
    u = create_test_user()
    new_password = "qwerty123Q"

    # Then
    security = Security.change_password(user_id=u.id,
                                        current_password=Data.TEST_PASSWORD,
                                        new_password=new_password)

    # When
    assert security
    assert security.get("message")


def test_security_change_password_2(prepopulated_session):
    """Test change user security password scenario negative: Wrong password"""
    # Given
    u = create_test_user()
    new_password = "qwerty123Q"
    old_hash = Security.get_user_password_hash(user_id=u.id)
    # Then
    with pytest.raises(UserError, match="Invalid password"):
        security = Security.change_password(user_id=u.id,
                                            current_password=new_password,
                                            new_password=new_password)

    # When
    with pytest.raises(UnboundLocalError):
        assert security
    new_hash = Security.get_user_password_hash(user_id=u.id)
    assert old_hash == new_hash


def test_security_change_password_3(prepopulated_session):
    """Test change user security password scenario negative: User not found"""
    # Given
    new_password = "qwerty123Q"
    # Then
    with pytest.raises(NotFoundError, match="Password not found"):
        security = Security.change_password(user_id=999,
                                            current_password=new_password,
                                            new_password=new_password)

    # When
    with pytest.raises(UnboundLocalError):
        assert security


def test_get_password_hash_1(prepopulated_session):
    """Test change user security password scenario success"""
    # Given
    u = create_test_user()

    # When
    result = Security.get_user_password_hash(u.id)

    # Then
    assert result


def test_get_password_hash_2(prepopulated_session):
    """Test change user security password scenario negative: Password hash for User not found"""

    # Given, When, Then
    with pytest.raises(NotFoundError, match="Password hash for User not found"):
        Security.get_user_password_hash(9999)
