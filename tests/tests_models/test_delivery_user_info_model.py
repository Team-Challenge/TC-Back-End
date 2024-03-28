import pytest

from models.accounts import DeliveryUserInfo
from models.errors import NotFoundError
from tests.conftest import TestValidData as Data, create_test_user


def create_delivery_info(user_id: int):
    delivery_info = DeliveryUserInfo.add_delivery_info(user_id=user_id,
                                                       post=Data.TEST_POST,
                                                       city=Data.TEST_CITY,
                                                       branch_name=Data.TEST_BRANCH_NAME,
                                                       address=Data.TEST_ADDRESS)
    return delivery_info


def test_add_delivery_info_1(prepopulated_session):
    """Test create delivery info scenario success"""
    # Given
    u = create_test_user()

    # When
    result = create_delivery_info(user_id=u.id)

    # Then
    assert result
    assert result[0].get("message") == "Delivery address created successfully"

    delivery_info: DeliveryUserInfo = DeliveryUserInfo.query.filter_by(owner_id=u.id).first()
    assert delivery_info.owner == u
    assert delivery_info.owner_id == u.id
    assert delivery_info.post == Data.TEST_POST
    assert delivery_info.city == Data.TEST_CITY
    assert delivery_info.branch_name == Data.TEST_BRANCH_NAME
    assert delivery_info.address == Data.TEST_ADDRESS


def test_add_delivery_info_2(prepopulated_session):
    """Test update delivery info using create method, scenario success"""
    # Given
    u = create_test_user()
    new_post = "New Post"
    new_city = "New City"
    new_branch = "New Branch"
    new_address = "New Address"
    result = DeliveryUserInfo(owner_id=u.id,
                              post=Data.TEST_POST,
                              city=Data.TEST_CITY,
                              branch_name=Data.TEST_BRANCH_NAME,
                              address=Data.TEST_ADDRESS)
    prepopulated_session.add(result)
    prepopulated_session.commit()
    assert result.id

    # When
    result = DeliveryUserInfo.add_delivery_info(user_id=u.id,
                                                post=new_post,
                                                city=new_city,
                                                branch_name=new_branch,
                                                address=new_address)
    # Then
    assert result
    assert result[0].get("message") == "Delivery address updated successfully"

    delivery_info: DeliveryUserInfo = DeliveryUserInfo.query.filter_by(owner_id=u.id).first()
    assert delivery_info.post == new_post
    assert delivery_info.city == new_city
    assert delivery_info.branch_name == new_branch
    assert delivery_info.address == new_address


def test_add_delivery_info_3(prepopulated_session):
    """Test create delivery info scenario negative: User not found"""
    # Given
    wrong_user_id = 999
    # When
    with pytest.raises(NotFoundError, match="User not found"):
        result = create_delivery_info(wrong_user_id)

    # Then
    with pytest.raises(UnboundLocalError):
        assert result
    data = DeliveryUserInfo.query.filter_by(owner_id=wrong_user_id).first()
    assert data is None


def test_get_delivery_info_by_owner_id(prepopulated_session):
    """Test get delivery info by user id scenario success"""
    # Given
    u = create_test_user()
    create_delivery_info(u.id)

    # When
    result = DeliveryUserInfo.get_delivery_info_by_owner_id(u.id)

    # Then
    assert result
    assert result.owner == u
    assert result.owner_id == u.id
    assert result.post == Data.TEST_POST
    assert result.city == Data.TEST_CITY
    assert result.branch_name == Data.TEST_BRANCH_NAME
    assert result.address == Data.TEST_ADDRESS


def test_update_delivery_info_1(prepopulated_session):
    """Test update delivery info scenario success"""
    # Given
    u = create_test_user()
    create_delivery_info(u.id)
    delivery_info = DeliveryUserInfo.get_delivery_info_by_owner_id(u.id)
    new_post = "New Post"
    new_city = "New City"
    new_branch = "New Branch"
    new_address = "New Address"

    # When
    delivery_info.update_delivery_info(post=new_post, city=new_city, branch_name=new_branch, address=new_address)

    # Then
    delivery_info = DeliveryUserInfo.get_delivery_info_by_owner_id(u.id)
    assert delivery_info.post == new_post
    assert delivery_info.city == new_city
    assert delivery_info.branch_name == new_branch
    assert delivery_info.address == new_address


def test_remove_delivery_info_1(prepopulated_session):
    """Test to remove delivery info scenario success"""
    # Given
    u = create_test_user()
    create_delivery_info(u.id)

    # When
    result = DeliveryUserInfo.remove_delivery_info(user_id=u.id)

    # Then
    assert result
    assert result.get("message") == "Delivery address removed successfully"
    delivery_info = DeliveryUserInfo.query.filter_by(owner_id=u.id).first()
    assert delivery_info is None


def test_remove_delivery_info_2(prepopulated_session):
    """Test to remove delivery info scenario negative: Delivery address not found"""
    # Given
    u = create_test_user()

    # When
    with pytest.raises(NotFoundError, match="Delivery address not found"):
        result = DeliveryUserInfo.remove_delivery_info(user_id=u.id)

    # Then
    with pytest.raises(UnboundLocalError):
        assert result


def test_remove_delivery_info_3(prepopulated_session):
    """Test to remove delivery info scenario negative: User not found"""
    # Given

    # When
    with pytest.raises(NotFoundError, match="User not found"):
        result = DeliveryUserInfo.remove_delivery_info(user_id=999)

    # Then
    with pytest.raises(UnboundLocalError):
        assert result
