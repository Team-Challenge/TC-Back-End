# import json
from pathlib import Path

from flask import json
import pytest
from sqlalchemy.orm import sessionmaker
from app import create_testing_app
from dependencies import db
from config.config import TestConfig
from tests import status
from data.create_fixtures import create_fixture_t
BASE_DIR = Path(__file__).resolve().parent.parent

N = 0


def get_payload():
    global N
    N += 1
    payload = {
        "email": f"test_test@{N}example.com",
        "full_name": "Testname testlastname",
        "password": "Password123"
    }
    return payload

def authorize(client, refresh=False):
    valid_signup_data = get_payload()
    client.post('/accounts/signup', data=json.dumps(valid_signup_data),
                content_type='application/json')
    valid_signup_data.pop("full_name")
    valid_signin_data = valid_signup_data
    response = client.post('/accounts/signin', data=json.dumps(valid_signin_data),
                           content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
    assert response.get_json().get("access_token")

    # Authorization using token
    if refresh:
        access_token = response.get_json().get("refresh_token")
    else:
        access_token = response.get_json().get("access_token")
    headers = {'Authorization': f'Bearer {access_token}'}
    return headers, valid_signup_data


def orint(*args):
    print("\n-------------------------------------------")
    for arg in args:
        print(arg)
    print("-------------------------------------------")


@pytest.fixture()
def app():
    app = create_testing_app(config_class=TestConfig)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def engine(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield db.engine
        db.drop_all()


@pytest.fixture(scope='function')
def session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope='function')
def prepopulated_engine(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope="function")
def prepopulated_session(prepopulated_engine):
    Session = sessionmaker(bind=prepopulated_engine.engine)
    session = Session()
    create_fixture_t(prepopulated_engine)
    yield session
    session.rollback()
    session.close()