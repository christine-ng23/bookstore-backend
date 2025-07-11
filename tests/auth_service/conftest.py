## tests/auth_service/conftest.py
import pytest

from auth_service.config import CLIENT_ID, CLIENT_SECRET
from auth_service.db import get_session
from common.config import TEST_SECRET_KEY
from test_utils.data_loader import clean_data, initialize_data_from_json

from tests.auth_service.api.pages.auth_api import AuthAPI
from tests.auth_service.api.pages.reset_api import ResetAPI

AUTH_BASE_URL = "http://localhost:5000"
BOOK_BASE_URL = "http://localhost:5001"

@pytest.fixture(scope="session")
def auth_api(request):
    # param = getattr(request, "param", {})
    # # Reset and load data
    # json_file = param.get("json_file", None)
    # session = get_session()
    # clean_data(session)
    # if json_file:
    #     initialize_data_from_json(session, json_file)
    yield AuthAPI(AUTH_BASE_URL)


@pytest.fixture(scope="session")
def reset_api():
    yield ResetAPI(BOOK_BASE_URL, TEST_SECRET_KEY)


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
