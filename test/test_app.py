import os
import tempfile

import pytest

from app import create_app, db
from test_config import Config


@pytest.fixture
def app():
    app = create_app(Config)
    app.config.update({
        "TESTING": True,
    })
    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

def test_signup(client):
    response = client.post("/accounts/signup", json={
        "full_name": "Alex",
        "email": "alex@gmail.com",
        "password": "1222add1"
    })
    assert response.status_code == 200


def test_signin(client):
    response = client.post("/accounts/signin", json={
        "email": "alex@gmail.com",
        "password": "1222add1"
    })
    assert response.status_code == 200