# tests/auth_service/api/test_api_reset_load.py
import os
import json
import tempfile

import pytest

# Configuration
VALID_DATA = {
    "users": [{"username": "admin", "password": "admin", "role": "admin"}],
    "books": [],
    "orders": []
}

def test_reset_with_json_body(reset_api):
    res = reset_api.reset_with_json(VALID_DATA)
    assert res.status_code == 200
    assert res.json() == {"status": "success"}


def test_reset_with_uploaded_file(reset_api):
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
        json.dump(VALID_DATA, f)
        f.flush()
        res = reset_api.reset_with_file(f.name)
        os.unlink(f.name)

    assert res.status_code == 200
    assert res.json() == {"status": "success"}


def test_reset_missing_auth(reset_api):
    res = reset_api.reset_without_auth(VALID_DATA)
    assert res.status_code == 401
    assert res.json() == {"error": "Unauthorized"}


def test_reset_invalid_auth(reset_api):
    res = reset_api.reset_with_invalid_auth(VALID_DATA)
    assert res.status_code == 401
    assert res.json() == {"error": "Unauthorized"}


def test_reset_invalid_file_type(reset_api):
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
        f.write("this is not JSON")
        f.flush()
        res = reset_api.reset_with_invalid_ext(f.name)
        os.unlink(f.name)

    assert res.status_code == 400
    assert "Uploaded file must be a .json file" in res.json().get("error", "")



def test_reset_missing_body_and_file(reset_api):
    res = reset_api.reset_without_file_and_json()
    assert res.status_code == 400
    assert "Must upload JSON file or send JSON body" in res.json().get("error", "")
