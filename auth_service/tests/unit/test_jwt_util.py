## auth_service/tests/unit/test_jwt_util.py
from datetime import datetime, timezone

import jwt
import pytest
from jwt import DecodeError, ExpiredSignatureError

from auth_service.config import SECRET
from auth_service.token_utils import generate_token, verify_token, timedelta


def test_generate_token_and_verify():
    expected_payload = {"user_id": 1, "role": "admin"}
    token = generate_token(expected_payload)
    payload = verify_token(token)
    assert payload["user_id"] == expected_payload["user_id"]
    assert payload["role"] == expected_payload["role"]


def test_generate_token_and_verify_empty():
    expected_payload = {}
    token = generate_token(expected_payload)
    payload = verify_token(token)
    assert len(payload.keys()) == 1 and "exp" in payload.keys()


def test_verify_token_expired():
    expired_token = jwt.encode(
        {"user_id": 2, "role": "user", "exp": datetime.now(timezone.utc) + timedelta(minutes=-1)},
        SECRET, algorithm="HS256")
    with pytest.raises(ExpiredSignatureError, match="Signature has expired"):
        verify_token(expired_token)


def test_verify_token_invalid():
    with pytest.raises((ValueError, DecodeError)):
        verify_token("not-a-token")
