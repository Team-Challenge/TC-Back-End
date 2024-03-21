import pytest
from sqlalchemy.exc import IntegrityError

from models.products import Categories


def test_create_category_1(session):
    """Test create category scenario success"""
    # Given
    category_name = "Sample Name"
    # When
    response = Categories.create_category(category_name)

    assert response
    assert response.id > 0
    assert response.category_name == category_name


def test_get_all_categories_1(session):
    """Test to create multiple categories and return them all, scenario success"""
    # Given
    category_name = "Sample Name"
    # When
    categories = []
    for i in range(0, 15):
        categories.append(Categories.create_category(f'{category_name}_{i + 1}'))

    # Then

    result = Categories.query.all()
    assert len(categories) == len(result)

    for created, found in zip(categories, result):
        assert created.category_name == found.category_name
    assert len(session.query(Categories).all()) == 15


def test_get_all_categories_2(session):
    """Test to create multiple categories and return them all, scenario negative: Unique constraint"""
    # Given
    category_name = "Sample Name"
    Categories.create_category(category_name)

    # When
    with pytest.raises(IntegrityError):
        Categories.create_category(category_name)

    result = session.query(Categories).all()
    assert len(result) == 1
    assert result[0].category_name == category_name
