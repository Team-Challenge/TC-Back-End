import os.path

from flask import json

from models.models import Categories
from tests import status
from tests.conftest import orint, authorize, get_payload, BASE_DIR


def test_get_categories(client, session):
    result = client.get("/categories/categories")

    assert result.status_code == status.HTTP_200_OK

    data: list = result.get_json()
    with open(os.path.join(BASE_DIR, "static/categories/categories.json"), encoding="utf-8") as file:
        categories_json = json.loads(file.read())
    assert len(data) == len(categories_json)
    for category in data:
        assert category.get("label")


def test_get_dynamic_categories(client, prepopulated_session):
    result = client.get("/categories/categories_detail")
    data = result.get_json()
    assert len(data) == 6
    assert data[0].get("label")
    assert data[0].get("subcategories")[0][0] == 11

    assert data[1].get("label")
    assert data[1].get("subcategories")[0][0] == 21

    assert data[2].get("label")
    assert data[2].get("subcategories")[0][0] == 31

    assert data[3].get("label")
    assert data[3].get("subcategories")[0][0] == 41

    assert data[4].get("label")
    assert data[4].get("subcategories")[0][0] == 51

    assert data[5].get("label")
    assert data[5].get("subcategories")[0][0] == 61