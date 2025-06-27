# tests/conftest.py
import pytest

from auth_service.config import CLIENT_ID, CLIENT_SECRET

from tests.auth_service.api.pages.auth_api import AuthAPI

TEST_AUTH_URL = "http://localhost:5000"

@pytest.fixture(scope="session")
def auth_api():
    yield AuthAPI(TEST_AUTH_URL)


@pytest.fixture(scope="session")
def user():
    return {"username": "admin", "password": "admin"}


@pytest.fixture(scope="session")
def code(auth_api, user):
    return auth_api.authorize(data={
        "username": user["username"],
        "password": user["password"]
    }).json()["code"]


@pytest.fixture(scope="session")
def admin_token(auth_api):
    auth_code = auth_api.authorize(data={
        "username": "admin",
        "password": "admin"
    }).json()["code"]

    res = auth_api.exchange_token(json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code
    })
    return res.json()["access_token"]



@pytest.fixture(scope="session")
def user_token(auth_api):
    auth_code = auth_api.authorize(data={
        "username": "user",
        "password": "pw"
    }).json()["code"]

    res = auth_api.exchange_token(json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code
    })
    return res.json()["access_token"]
