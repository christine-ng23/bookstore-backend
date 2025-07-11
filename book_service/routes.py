## book_service/routes.py
"""
Provide APIs for managing users, books, and orders
Each API Responsibilities:
    - Uses @require_auth to validate authorization header, return proper JSON error responses
    - Uses @require_role to validate the user role and return proper JSON error responses
    - Parse request JSON body
    - Validate JSON body for presence of required fields
    - Delegate full validation and creation to the service layer
    - Return a JSON response with created/updated/deleted/got info
    - Uses @handle_exceptions to catch and return proper JSON error responses
    - Order of validation: Auth -> Role -> Required fields -> Type
"""
from flask import Blueprint, request, jsonify, g, current_app

from auth_service.auth_middleware import require_auth, require_role
from .db import get_session
from .services.book_service import *
from .services.order_service import *
from .services.user_service import *
from .utils.handlers import handle_exceptions
books_bp = Blueprint('books', __name__)


@books_bp.route('/books')
def get_all_books():
    """
    GET /books

    Returns a list of all available books.

    Requirements: NA

    Response:
    - 200: List of book objects

   """
    with get_session() as session:
        return jsonify([b.to_dict() for b in list_books(session)]), 200


@books_bp.route('/books', methods=['POST'])
@handle_exceptions
@require_auth()
@require_role("admin")
def add_book_route():
    """
    POST /books

    Adds a new book to the inventory.

    Requirements:
    - Must be authenticated
    - Must have 'admin' role
    - JSON body must include fields: code, name.
    - Field types: "code": str, "name": str, "quantity": int, "publisher": str,
                                "imported_price": int or float, "sell_price": int or float
    - Non-negative fields: "imported_price", "sell_price"
    - Book code must unique
    Response:
    - 201: created successfully
    - 401: Unauthorized
    - 403: Insufficient permission
    - 400: Validation errors
    - 409: database integrity errors, for instance not unique book code
    """
    # Check for required fields
    data = request.get_json()
    required_fields = ['code', 'name']
    missing = [f for f in required_fields if not data.get(f)]

    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    with get_session() as session:
        return jsonify(add_book(session, data).to_dict()), 201


@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@handle_exceptions
@require_auth()
@require_role('admin')
def edit_book_route(book_id):
    """
    PUT /books/<book_id>

    Updates an existing book with new data.

    Requirements:
    - Must be authenticated
    - Must have 'admin' role
    - Non-empty if present fields: code, name.
    - Field types: "code": str, "name": str, "quantity": int, "publisher": str,
                                "imported_price": int or float, "sell_price": int or float
    - Non-negative fields: "imported_price", "sell_price"
    - Book code must unique

    Response:
    - 200: Book updated successfully
    - 401: Unauthorized
    - 403: Insufficient permission
    - 404: Book not found
    - 400: Validation error or invalid fields
    - 409: database integrity errors
    """
    with get_session() as session:
        return jsonify(update_book(session, book_id, request.json).to_dict()), 200


@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@handle_exceptions
@require_auth()
@require_role('admin')
def delete_book_route(book_id):
    """
    DELETE /books/<book_id>

    Deletes a book from the system.

    Requirements:
    - Must be authenticated
    - Must have 'admin' role
    - Book must be existed
    - Book must not in any orders

    Response:
    - 200: Book deleted successfully
    - 401: Unauthorized
    - 403: Insufficient permission
    - 404: Book not found
    - 409: database integrity errors: book_id FK constraint violation
    """
    with get_session() as session:
        return jsonify(delete_book(session, book_id).to_dict()), 200


@books_bp.route('/orders', methods=['POST'])
@handle_exceptions
@require_auth()
def place_order_route():
    """
    POST /orders

    Create a new order for books.

    Requirements:
    - Must be authenticated
    - JSON body must include items list, each items must has book_id, quantity
    - book_id must be existed, stock must be available
    {
        "items": [{
                "book_id": 1,
                "quantity": 3
            },{
                "book_id": 2,
                "quantity": 4
            }]
    }

    Response:
    - 201: created successfully return json response with order info
    - 401: Unauthorized
    - 400: Validation error (missing or invalid data violations)
    - 404: Book ID is not found
    - 400: Book stock unavailable
    - 409: database integrity errors
    """
    data = request.json
    if "items" not in data:
        return jsonify({"error": f"Missing required field: items"}), 400

    user_id = g.user['user_id']
    with get_session() as session:
        return jsonify(place_order(session, user_id, data['items']).to_dict()), 201


@books_bp.route('/orders')
@handle_exceptions
@require_auth()
def list_order_route():
    """
    GET /orders

    Returns the list of orders placed by the current user.

    Requirements:
    - Must be authenticated

    Response:
    - 200: List of order objects
    - 401: Unauthorized
    """
    is_admin = g.user['role'] == 'admin'
    user_id = g.user['user_id']
    with get_session() as session:
        return jsonify([o.to_dict() for o in list_orders(session, user_id=user_id, is_admin=is_admin)]), 200


@books_bp.route('/orders/<int:oid>/status', methods=['PUT'])
@handle_exceptions
@require_auth()
def update_order_route(oid):
    """
    PUT /orders/<order_id>

    Updates order details such as status or quantity.

    Requirements:
    - Must be authenticated
    - Must be admin, or order owner. Order owner only able to update status from "new" to "canceled"
    - Update-able fields: "status"
    - Non-empty field if present: "status"
    - Field types: "status": str

    Response:
    - 200: Order updated successfully
    - 401: Unauthorized
    - 404: Order not found
    - 400: Validation error or illegal update (violate status transitions)
    - 403: user does not have permission for the status update
    - 409: DB check violation (e.g., FK, constraints)

    """
    is_admin = g.user['role'] == 'admin'
    user_id = g.user['user_id']
    data = request.json
    if not data.get("status"):
        return jsonify({"error": "Missing required field: status"}), 400

    with get_session() as session:
        return jsonify(update_order_status(session, oid, data["status"], user_id, is_admin).to_dict()), 200


@books_bp.route('/users')
@handle_exceptions
@require_auth()
@require_role("admin")
def list_all_users():
    """
    GET /users

    Returns a list of all users in the system.

    Requirements:
    - Must be authenticated
    - Must have 'admin' role

    Response:
    - 200: List of user objects
    - 401: Unauthorized (handled in require_auth)
    - 403: Forbidden (handled in require_role)
    """
    with get_session() as session:
        return jsonify([u.to_dict() for u in list_users(session)])


@books_bp.route('/users', methods=['POST'])
@handle_exceptions
@require_auth(optional=True)
def register_user_route():
    """
    POST /users

    Handle user registration.

    Requirements:
    - Required fields: 'username' and 'password'
    - Field type: 'username': str, 'password': str, 'role': str
    - 'username' contains only alphanumeric, underscore, dot, hyphen
    - 'role' value must be valid

    Response:
    - 201: created successfully return json response with user info
    - 400: required fields, validation errors, username not unique
    - 409: database integrity errors
    """
    # Check for required fields
    data = request.get_json()
    required_fields = ['username', 'password']
    missing = [f for f in required_fields if not data.get(f)]

    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    is_admin = g.user is not None and g.user.get("role") == Roles.ADMIN
    with get_session() as session:
        return jsonify({
            "message": "User registered successfully",
            "user": register_user(session, data, is_admin=is_admin).to_dict()
        }), 201
