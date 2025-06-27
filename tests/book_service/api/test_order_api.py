# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NTQ1MDYwNjZ9.-aFIS-9CadGECem5c61XnqUA8AdrlvmkFg_1m6mQFjo
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJyb2xlIjoidXNlciIsImV4cCI6MTc1NDUwNjMxNn0.oi0dPczTe4HWbb70H4Q7LlmlISwCipAeqpynL2aPTHc
## tests/book_service/api/test_order_api.py
import pytest

from common.constants import TEST_SESSION_TYPE, ORDER_TRANSITIONS, OrderStatus
from common.utils import assert_json_structure


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_list_order_success_all_orders(client, admin_auth_header):
    """
        Response 200
            {order_info}
    """
    res = client.get("/orders", headers=admin_auth_header)
    # Verify response code and json body
    assert res.status_code == 200
    orders = res.json
    assert isinstance(orders, list)
    assert len(orders) == 9
    for order in orders:
        assert_json_structure(order, {"id": int, "user_id": int, "items": list})


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_list_order_success_users_belonging_orders(client, user_auth_header):
    """
        Response 200
            {order_info}
    """
    res = client.get("/orders", headers=user_auth_header)
    # Verify response code and json body
    assert res.status_code == 200
    orders = res.json
    assert isinstance(orders, list)
    assert len(orders) == 7
    for order in orders:
        assert_json_structure(order, {"id": int, "user_id": int, "items": list})


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_list_order_unsuccessful_unauthorized(client):
    """
    Response 401
        {
            "error": "Authorization header missing or invalid"
        }

    """
    res = client.get("/orders")
    # Verify response code and json body
    assert res.status_code == 401
    assert res.json == {
        "error": "Authorization header missing or invalid"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_success(client, admin_auth_header):
    """
    Response 201
    {
        "created_at": "<datetime>",
        "id": <id>,
        "items": [
            {
                "book_id": 1,
                "id": <orderitem_id>,
                "order_id": <id>,
                "price_each": <book_sellprice>,
                "quantity": 10
            }
        ],
        "status": "new",
        "user_id": <user_id>
    }
    """
    order_data = {
        "items": [
            {
                "book_id": 1,
                "quantity": 10            },
            {
                "book_id": 2,
                "quantity": 15
            }
        ]
    }
    res = client.post("/orders", json=order_data, headers=admin_auth_header)
    # Verify response code and json body
    assert res.status_code == 201
    order_info = res.json
    expected_order_id = 1
    assert isinstance(order_info, dict)
    assert order_info["id"] == expected_order_id
    assert order_info["user_id"] == 1
    assert order_info["status"] == "new"
    items = order_info["items"]
    for i, item in enumerate(items):
        expected_item = order_data["items"][i]
        assert_json_structure(item, {"book_id": int, "id": int, "order_id": int,
                                     "price_each": (int, float), "quantity": int})
        assert item["order_id"] == expected_order_id
        assert all(expected_item[f] == item[f] for f in expected_item)


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_place_order_unsuccessful_unauthorized(client):
    """
    Response 401
        {
            "error": "Authorization header missing or invalid"
        }

    """
    order_data = {
        "items": [
            {
                "book_id": 1,
                "quantity": 10
            }
        ]
    }
    res = client.post("/orders", json=order_data)
    # Verify response code and json body
    assert res.status_code == 401
    assert res.json == {
        "error": "Authorization header missing or invalid"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_unsuccessful_missing_fields_items(client, user_auth_header):
    """
    Response 400
        {
            "error": "Missing required field: items"
        }
    """
    order_data = {}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Missing required field: items"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_unsuccessful_incorrect_fields_type_items(client, user_auth_header):
    """
    Response 400
        {
            "error": "Type error: Argument 'items' must be of type list, got {other_type}"
        }
    """
    # Incorrect type: type dict
    order_data = {"items": {}}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Type error: Argument 'items' must be of type list, got dict"
        }

    # Incorrect type: type str
    order_data = {"items": ""}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
        "error": "Type error: Argument 'items' must be of type list, got str"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_unsuccessful_incorrect_fields_type_items(client, user_auth_header):
    """
    Response 400
        {
            "error": "Items can not empty"
        }
    """
    order_data = {"items": []}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Items can not empty"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_unsuccessful_missing_items_subfields(client, user_auth_header):
    """
    Response 400
        {
            "error": "Missing required field: book_id; Missing required field: quantity"
        }
    """
    order_data = {"items": [{}]}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
        "error": "Missing required field: book_id; Missing required field: quantity"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_unsuccessful_invalid_items_subfields_types(client, user_auth_header):
    """
    Response 400
        {
            "error": "Field 'book_id' must be of type int; Field 'quantity' must be of type int"
        }
    """
    order_data = {"items": [{
            "book_id": "1",
            "quantity": "10",
            "price_each": "110"
        }]}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
        "error": "Field 'book_id' must be of type int; Field 'quantity' must be of type int"
    }

@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_unsuccessful_invalid_non_negative_items_subfields(client, user_auth_header):
    """
    Response 400
        {
            "error": "Field 'book_id' must be non-negative; Field 'quantity' must be non-negative"
        }
    """
    order_data = {"items": [{
            "book_id": -1,
            "quantity": -10
        }]}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
        "error": "Field 'book_id' must be non-negative; Field 'quantity' must be non-negative"
    }

@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_unsuccessful_non_existed_book_id(client, user_auth_header):
    """
    Response 404
        {
            "error": "Book with id <book_id> not found"
        }
    """
    order_data = {"items": [{
            "book_id": 100,
            "quantity": 10,
            "price_each": 110
        }]}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 404
    assert res.json == {
        "error": "Book with id 100 not found"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed_users_books.json"}], indirect=True)
def test_place_order_unsuccessful_non_existed_book_id(client, user_auth_header):
    """
    Response 400
        {
            "error": "Book with id {book_id} quantity not enough"
        }
    """
    order_data = {"items": [{
            "book_id": 1,
            "quantity": 11,
            "price_each": 110
        }]}
    res = client.post("/orders", json=order_data, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
            "error": "Book with id 1 quantity not enough"
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_update_order_status_successful_by_admin_follow_status_transition(client, admin_auth_header):
    """
    Response 200
    {
        "created_at": "<datetime>",
        "id": <id>,
        "items": [
            {
                "book_id": 1,
                "id": <orderitem_id>,
                "order_id": <id>,
                "price_each": <book_sellprice>,
                "quantity": 10
            }
        ],
        "status": "new",
        "user_id": <user_id>
    }
    """
    orders = {"new": [1, 3, 4], "processing": [2,5], "shipping": [6], "delivered": [7], "canceled": [8], "rejected": [9]}
    for status in ORDER_TRANSITIONS:
        for i, next_status in enumerate(ORDER_TRANSITIONS[status]):
            status_update = {"status": next_status}
            order_id = orders[status][i]
            res = client.put(f"/orders/{order_id}/status", json=status_update, headers=admin_auth_header)
            # Verify response code and json body
            assert res.status_code == 200
            assert res.json["id"] == order_id
            assert res.json["status"] == next_status


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_update_order_status_successful_by_order_owner(client, user_auth_header):
    """
    Response 200
    {
        "created_at": "<datetime>",
        "id": <id>,
        "items": [
            {
                "book_id": 1,
                "id": <orderitem_id>,
                "order_id": <id>,
                "price_each": <book_sellprice>,
                "quantity": 10
            }
        ],
        "status": "new",
        "user_id": <user_id>
    }
    """
    status_update = {"status": "canceled"}
    res = client.put(f"/orders/3/status", json=status_update, headers=user_auth_header)
    # Verify response code and json body
    assert res.status_code == 200
    assert res.json["id"] == 3
    assert res.json["status"] == "canceled"


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_update_order_status_unsuccessful_missing_field_status(client, user_auth_header):
    """
    Response 400
        {
            "error": "Missing required field: status"
        }
    """
    status_update = {}
    res = client.put("/orders/100/status", json=status_update, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
        "error": "Missing required field: status"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE}], indirect=True)
def test_update_order_status_unsuccessful_invalid_field_type_status(client, user_auth_header):
    """
    Response 400
        {
            "error": "Type error: Argument 'status' must be of type str, got int"
        }
    """
    status_update = {"status": 123}
    res = client.put("/orders/100/status", json=status_update, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
        "error": "Type error: Argument 'status' must be of type str, got int"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_update_order_status_unsuccessful_non_existed_order_id(client, user_auth_header):
    """
    Response 404
        {
            "error": "Order with id <order_id> not found"
        }
    """
    status_update = {"status": "123"}
    res = client.put("/orders/100/status", json=status_update, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
        "error": "Order with id 100 not found"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_update_order_status_unsuccessful_non_existed_order_id(client, user_auth_header):
    """
    Response 400
        {
            "error": "status must be one of: canceled, delivered, new, processing, rejected, shipping"
        }
    """
    status_update = {
        "status": "invalid_value"
    }
    res = client.put("/orders/1/status", json=status_update, headers=user_auth_header)
    assert res.status_code == 400
    assert res.json == {
        "error": "status must be one of: canceled, delivered, new, processing, rejected, shipping"
    }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_update_order_status_unsuccessful_owner_can_only_reject_new_order(client, user_auth_header):
    """
    Response 403
        {
            "error": "You are not authorized to update this order."
        }
    """
    invalid_next_statuses = OrderStatus.ALL - {OrderStatus.NEW, OrderStatus.CANCELED}
    for status in invalid_next_statuses:
        status_update = {
            "status": status
        }
        res = client.put("/orders/3/status", json=status_update, headers=user_auth_header)
        assert res.status_code == 403
        assert res.json == {
                "error": "You are not authorized to update this order."
        }

@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_update_order_status_unsuccessful_non_owner_do_not_have_permission(client, user_auth_header):
    """
    Response 403
        {
            "error": "You are not authorized to update this order."
        }
    """
    for status in OrderStatus.ALL:
        status_update = {
            "status": status
        }
        res = client.put("/orders/1/status", json=status_update, headers=user_auth_header)
        assert res.status_code == 403
        assert res.json == {
                "error": "You are not authorized to update this order."
        }


@pytest.mark.parametrize("client", [{"type": TEST_SESSION_TYPE, "json_file": "test_seed.json"}], indirect=True)
def test_update_order_status_unsuccessful_violating_order_transition(client, admin_auth_header):
    """
    Response 403
        {
            "error": "You are not authorized to update this order."
        }
    """
    orders = {"new": [1, 3, 4], "processing": [2,5], "shipping": [6], "delivered": [7], "canceled": [8], "rejected": [9]}

    for current_status in OrderStatus.ALL:
        invalid_next_status = OrderStatus.ALL-set(ORDER_TRANSITIONS.get(current_status))
        for next_status in invalid_next_status:
            status_update = {"status": next_status}
            order_id = orders[current_status][0]
            res = client.put(f"/orders/{order_id}/status", json=status_update, headers=admin_auth_header)
            assert res.status_code == 400
            assert res.json == {
                    "error": f"Cannot change status from {current_status} to {next_status}"
            }
