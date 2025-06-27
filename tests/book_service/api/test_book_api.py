import pytest

from common.constants import TEST_SESSION_TYPE


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_list_books(client):
    """
    Response 200
        [ {book_info},]
    """
    books = [{
              "code": "B001",
              "name": "Python Basics",
              "publisher": "O'Reilly",
              "quantity": 10,
              "imported_price": 100,
              "sell_price": 110
            },
            {
              "code": "B002",
              "name": "Python Advanced",
              "publisher": "O'Reilly",
              "quantity": 15,
              "imported_price": 95.55,
              "sell_price": 100.55
            }]
    res = client.get("/books")
    assert res.status_code == 200
    # assert_json_structure(book, {"code": str, "name": str, "publisher": str, "quantity": int,
    #                              "imported_price": int, "sell_price": int})
    for i, book in enumerate(res.json):
        books[i] == res.json[i]


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_list_books_empty(client):
    """
    Response 200
        []
    """
    res = client.get("/books")
    assert res.status_code == 200
    assert isinstance(res.json, list) and not res.json


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_successful(client, admin_auth_header):
    """
    Response 201
        {book_info}
    """
    book_data = {"code": "B001", "id": 1, "name": "API Book", "publisher": "Pub", "quantity": 3, "imported_price": 80, "sell_price": 88}
    res = client.post("/books", json=book_data, headers=admin_auth_header)
    assert res.status_code == 201
    assert res.json == book_data


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_successful_with_required_fields(client, admin_auth_header):
    """
    Response 201
        {book_info}
    """
    book_data = {"code": "B001", "id": 1, "name": "API Book"}
    res = client.post("/books", json=book_data, headers=admin_auth_header)
    assert res.status_code == 201
    created_book = res.json
    assert isinstance(created_book, dict)
    for f in book_data:
        assert book_data[f] == created_book[f]


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_unsuccessful_missing_required_fields(client, admin_auth_header):
    """
    Response 400
        {
            "error": "Missing required fields",
            "fields": [
                "code",
                "name"
            ]
        }
    """
    book_data = {}
    res = client.post("/books", json=book_data, headers=admin_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Missing required fields",
            "fields": [
                "code",
                "name"
            ]
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_unsuccessful_incorrect_field_types(client, admin_auth_header):
    """
    Response 400
        {
            "error": "Field 'code' must be of type str; Field 'name' must be of type str;
                Field 'quantity' must be of type int; Field 'publisher' must be of type str;
                Field 'imported_price' must be of type int or float; Field 'sell_price' must be of type int or float"
        }

    "A book with this code already exists."
    """
    book_data = {
        "code": 1,
        "name": 1,
        "publisher": 1,
        "quantity": "3",
        "imported_price": "80",
        "sell_price": "88"
    }
    res = client.post("/books", json=book_data, headers=admin_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Field 'code' must be of type str; Field 'name' must be of type str; "
                "Field 'quantity' must be of type int; Field 'publisher' must be of type str; "
                "Field 'imported_price' must be of type int or float; Field 'sell_price' must be of type int or float"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_unsuccessful_non_negative_fields(client, admin_auth_header):
    """
    Response 400
        {
            "error": "Field 'quantity' must be non-negative; Field 'imported_price' must be non-negative; Field 'sell_price' must be non-negative"
        }
    """
    book_data = {
        "code": "B001",
        "name": "API Book",
        "publishers": "Pub",
        "quantity": -3,
        "imported_price": -80,
        "sell_price": -88
    }
    res = client.post("/books", json=book_data, headers=admin_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Field 'quantity' must be non-negative; Field 'imported_price' must be non-negative;"
                     " Field 'sell_price' must be non-negative"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_add_book_unsuccessful_non_unique_code(client, admin_auth_header):
    """
    Response 400
        {
            "error": "A book with this code already exists."
        }

    """
    book_data = {
        "code": "B001",
        "name": "API Book"
    }
    res = client.post("/books", json=book_data, headers=admin_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "A book with this code already exists."
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_unsuccessful_unauthorized(client):
    """
    Response 401
        {
            "error": "Authorization header missing or invalid"
        }

    """
    res = client.post("/books", json={})
    assert res.status_code == 401
    assert res.json == {
            "error": "Authorization header missing or invalid"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_unsuccessful_insufficient_permission(client, user_auth_header):
    """
    Response 401
        {
            "error": "Forbidden: insufficient permission"
        }

    """
    res = client.post("/books", json={}, headers=user_auth_header)
    assert res.status_code == 403
    assert res.json == {
            "error": "Forbidden: insufficient permission"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_successful(client, admin_auth_header):
    """
    Response 200
        {book_info}
    """
    update_data = {
      "code": "B003",
      "name": "Python Experts",
      "publisher": "New Publisher",
      "quantity": 20,
      "imported_price": 200.55,
      "sell_price": 220.55
    }
    res = client.put("/books/1", json=update_data, headers=admin_auth_header)
    assert res.status_code == 200
    updated_book = res.json
    assert isinstance(updated_book, dict)
    for f in update_data:
        assert update_data[f] == updated_book[f]


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_successful_with_non_empty_if_present_fields_code(client, admin_auth_header):
    """
    Response 200
        {book_info}
    """
    update_data = {
        "code": "B003"
    }
    res = client.put("/books/1", json=update_data, headers=admin_auth_header)
    assert res.status_code == 200
    updated_book = res.json
    assert isinstance(updated_book, dict)
    for f in update_data:
        assert update_data[f] == updated_book[f]


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_successful_with_non_empty_if_present_fields_name(client, admin_auth_header):
    """
    Response 200
        {book_info}
    """
    update_data = {
        "name": "Python Experts"
    }
    res = client.put("/books/1", json=update_data, headers=admin_auth_header)
    assert res.status_code == 200
    updated_book = res.json
    assert isinstance(updated_book, dict)
    for f in update_data:
        assert update_data[f] == updated_book[f]


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_successful_with_non_empty_if_present_fields_all(client, admin_auth_header):
    """
    Response 200
        {book_info}
    """
    update_data = {
        "code": "B003",
        "name": "Python Experts"
    }
    res = client.put("/books/1", json=update_data, headers=admin_auth_header)
    assert res.status_code == 200
    updated_book = res.json
    assert isinstance(updated_book, dict)
    for f in update_data:
        assert update_data[f] == updated_book[f]


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_unsuccessful_unauthorized(client):
    """
    Response 401
        {
            "error": "Authorization header missing or invalid"
        }

    """
    res = client.put("/books/1", json={})
    assert res.status_code == 401
    assert res.json == {
            "error": "Authorization header missing or invalid"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_unsuccessful_insufficient_permission(client, user_auth_header):
    """
    Response 401
        {
            "error": "Forbidden: insufficient permission"
        }

    """
    res = client.put("/books/1", json={}, headers=user_auth_header)
    assert res.status_code == 403
    assert res.json == {
            "error": "Forbidden: insufficient permission"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_unsuccessful_with_non_existed_book_id(client, admin_auth_header):
    """
    Response 404
        {
            "error": "Book with id 3 not found"
        }
    """
    res = client.put("/books/3", json={}, headers=admin_auth_header)
    assert res.status_code == 404
    assert res.json == {
            "error": "Book with id 3 not found"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_unsuccessful_missing_non_empty_fields(client, admin_auth_header):
    """
    Response 400
        {
            "error": "Missing required field: code; Missing required field: name"
        }
    """
    book_data = {
        "code": "",
        "name": ""
    }
    res = client.put("/books/1", json=book_data, headers=admin_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Missing required field: code; Missing required field: name"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_unsuccessful_incorrect_field_types(client, admin_auth_header):
    """
    Response 400
        {
            "error": "Field 'code' must be of type str; Field 'name' must be of type str;
                Field 'quantity' must be of type int; Field 'publisher' must be of type str;
                Field 'imported_price' must be of type int or float; Field 'sell_price' must be of type int or float"
        }

    "A book with this code already exists."
    """
    book_data = {
        "code": 1,
        "name": 1,
        "publisher": 1,
        "quantity": "3",
        "imported_price": "80",
        "sell_price": "88"
    }
    res = client.put("/books/1", json=book_data, headers=admin_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Field 'code' must be of type str; Field 'name' must be of type str; "
                "Field 'quantity' must be of type int; Field 'publisher' must be of type str; "
                "Field 'imported_price' must be of type int or float; Field 'sell_price' must be of type int or float"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_unsuccessful_non_negative_fields(client, admin_auth_header):
    """
    Response 400
        {
            "error": "Field 'quantity' must be non-negative; Field 'imported_price' must be non-negative; Field 'sell_price' must be non-negative"
        }
    """
    book_data = {
        "quantity": -3,
        "imported_price": -80,
        "sell_price": -88
    }
    res = client.put("/books/1", json=book_data, headers=admin_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Field 'quantity' must be non-negative; Field 'imported_price' must be non-negative;"
                     " Field 'sell_price' must be non-negative"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_edit_book_unsuccessful_non_unique_code(client, admin_auth_header):
    """
    Response 400
        {
            "error": "A book with this code already exists."
        }
    """
    book_data = {
        "code": "B002",
    }
    res = client.put("/books/1", json=book_data, headers=admin_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "A book with this code already exists."
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_delete_book_successful(client, admin_auth_header):
    """
    Response 200
        { book_info }
    """
    res = client.delete("/books/1", headers=admin_auth_header)
    assert res.status_code == 200
    assert isinstance(res.json, dict)
    assert res.json["id"] == 1


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_delete_book_unsuccessful_non_existed_book_id(client, admin_auth_header):
    """
    Response 404
        {
            "error": "Book with id 3 not found"
        }
    """
    res = client.delete(f"/books/3", headers=admin_auth_header)
    assert res.status_code == 404
    assert res.json == {
            "error": "Book with id 3 not found"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_unsuccessful_unauthorized(client):
    """
    Response 401
        {
            "error": "Authorization header missing or invalid"
        }

    """
    res = client.delete("/books/1")
    assert res.status_code == 401
    assert res.json == {
            "error": "Authorization header missing or invalid"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_add_book_unsuccessful_insufficient_permission(client, user_auth_header):
    """
    Response 401
        {
            "error": "Forbidden: insufficient permission"
        }

    """
    res = client.delete("/books/1", headers=user_auth_header)
    assert res.status_code == 403
    assert res.json == {
            "error": "Forbidden: insufficient permission"
        }
