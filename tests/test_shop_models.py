import pytest
from sqlalchemy.exc import IntegrityError
from models.accounts import User
from models.errors import NotFoundError
from models.shops import Shop
from tests.conftest import TestValidData as Data


def create_test_user(email=Data.TEST_EMAIL,
                     full_name=Data.TEST_FULL_NAME,
                     password=Data.TEST_PASSWORD):
    u = User.create_user(email, full_name, password)
    return u


def create_test_shop(name=Data.TEST_SHOP_NAME,
                     description=Data.TEST_SHOP_DESCRIPTION,
                     phone_number=Data.TEST_SHOP_PHONE_NUMBER,
                     link=Data.TEST_SHOP_LINK):
    u = create_test_user()
    s = Shop.create_shop(owner_id=u.id,
                         name=name,
                         description=description,
                         phone_number=phone_number,
                         link=link)
    return s


def test_create_shop_1(session):
    """Test create shop scenario success """
    # Given
    owner_id = create_test_user().id
    name = "Shop name"
    description = "Best shop description"
    phone_number = "+380991122333"
    link = "insta.net"

    # When
    s = Shop.create_shop(owner_id=owner_id,
                         name=name,
                         description=description,
                         phone_number=phone_number,
                         link=link)

    # Then
    assert s
    assert s.id > 0
    assert s.owner_id == s.owner_id
    assert s is not None
    assert s.name == name
    assert s.description == description
    assert s.phone_number == phone_number
    assert s.link == link


def test_create_shop_2(session):
    """Test create shop scenario negative: Invalid name """
    # Given
    owner_id = create_test_user().id
    name = None
    description = "Best shop description"
    phone_number = "+380991122333"

    # When
    with pytest.raises(IntegrityError):
        s = Shop.create_shop(owner_id=owner_id,
                             name=name,
                             description=description,
                             phone_number=phone_number)

        # Then
        assert s is None


def test_create_shop_3(session):
    """Test create shop scenario negative: Invalid phone_number """
    # Given
    owner_id = create_test_user().id
    name = "Shop name"
    description = "Best shop description"
    phone_number = None

    # When
    with pytest.raises(IntegrityError):
        s = Shop.create_shop(owner_id=owner_id,
                             name=name,
                             description=description,
                             phone_number=phone_number)

        # Then
        assert s is None


def test_shop_by_owner_id_1(session):
    """Test get shop by owner_id success"""
    # Given
    s = create_test_shop()

    # When
    shop = Shop.get_shop_by_owner_id(owner_id=s.owner_id)

    # Then
    assert shop
    assert shop.id > 0
    assert shop.owner_id == s.owner_id
    assert shop is not None


def test_shop_by_owner_id_2(session):
    """Test get shop id scenario negative: Non-existent user"""
    # Given
    user_id = 999999

    # When
    shop = Shop.get_shop_by_owner_id(owner_id=user_id)

    # Then
    assert shop is None


def test_update_shop_info_1(session):
    """Test update shop info success"""
    # Given
    s = create_test_shop()

    # When
    s.update_shop_details(link="new link",
                          phone_number="+380974455566",
                          name="new name",
                          description="new description")

    # Then
    assert s.link == "new link"
    assert s.phone_number == "+380974455566"


def test_update_shop_info_2(session):
    """Test update shop scenario negative: Invalid phone_number or shop name """
    # Given
    s = create_test_shop()

    # When
    s.update_shop_details(phone_number=None, name=None)

    # Then
    assert s.phone_number == Data.TEST_SHOP_PHONE_NUMBER
    assert s.name == Data.TEST_SHOP_NAME


def test_get_shop_user_info_1(session):
    """Test get shop info success"""
    # Given
    s = create_test_shop()

    # When
    result = Shop.get_shop_user_info(s.owner_id)

    # Then
    assert result
    assert result.get("id")
    assert result.get("name") == Data.TEST_SHOP_NAME
    assert result.get("description") == Data.TEST_SHOP_DESCRIPTION
    assert result.get("photo_shop") is None
    assert result.get("banner_shop") is None
    assert result.get("phone_number") == Data.TEST_SHOP_PHONE_NUMBER
    assert result.get("link") == Data.TEST_SHOP_LINK


def test_get_shop_user_info_negative(session):
    """Test get shop info scenario negative: Non-existent user"""
    # Given
    non_existent_user_id = 9999

    # When
    with pytest.raises(NotFoundError, match="Shop not found"):
        Shop.get_shop_user_info(non_existent_user_id)
