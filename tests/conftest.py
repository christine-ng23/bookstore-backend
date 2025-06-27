from datetime import datetime, timezone, timedelta

import jwt
import pytest

from auth_service.config import SECRET
from auth_service.token_utils import generate_token


@pytest.fixture
def admin_auth_header():
    token = generate_token({"user_id": 1, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_header_expired():
    payload = {"user_id": 1, "role": "admin", "exp": datetime.now(timezone.utc) + timedelta(minutes=-1)}
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_auth_header():
    token = generate_token({"user_id": 2, "role": "user"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_not_bear():
    return {"Authorization": "not-bear-token"}


@pytest.fixture
def auth_header_empty_token():
    return {"Authorization": "Bearer "}


@pytest.fixture
def auth_header_invalid_token():
    return {"Authorization": "Bearer not-a-token"}


@pytest.fixture
def auth_header_payload_missing_user_id():
    token = generate_token({"role": "user"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_payload_missing_role():
    token = generate_token({"user_id": 1})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_auth_header_expired():
    payload = {"user_id": 2, "role": "user", "exp": datetime.now(timezone.utc) + timedelta(minutes=-1)}
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return {"Authorization": f"Bearer {token}"}

