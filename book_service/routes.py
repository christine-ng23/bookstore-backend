## book_service/routes.py
import jwt
from flask import Blueprint, request, jsonify, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth_service.config import SECRET
from auth_service.auth_middleware import require_auth, require_role
from common.constants import DB_PATH
from .services.book_service import *
from .services.order_service import *
from .services.user_service import *
from .utils.handlers import handle_exceptions

Session = sessionmaker(bind=create_engine(f'sqlite:///{DB_PATH}'))
books_bp = Blueprint('books', __name__)


def get_token_user():
    token = request.headers.get('Authorization', '').split()[-1]
    return jwt.decode(token, SECRET, algorithms=['HS256'])


@books_bp.route('/books')
@require_auth
def get_all_books():
    with Session() as session:
        return jsonify([b.to_dict() for b in list_books(session)])


@books_bp.route('/books', methods=['POST'])
@require_auth
@require_role("admin")
def add_book_route():
    # Check for required fields
    data = request.get_json()
    required_fields = ['code', 'name', 'imported_price', 'quantity']
    missing = [f for f in required_fields if not data.get(f)]

    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    with Session() as session:
        return jsonify(add_book(session, data).to_dict()), 201


@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@handle_exceptions
@require_auth
@require_role('admin')
def edit_book_route(book_id):
    with Session() as session:
        return jsonify(update_book(session, book_id, request.json).to_dict()), 201


@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@handle_exceptions
@require_auth
@require_role('admin')
def delete_book_route(book_id):
    with Session() as session:
        return jsonify(delete_book(session, book_id).to_dict()), 201


@books_bp.route('/orders', methods=['POST'])
@handle_exceptions
@require_auth
def place_order_route():
    with Session() as session:
        return jsonify(place_order(session, g.user['user_id'], request.json['items']).to_dict())


@books_bp.route('/orders')
@handle_exceptions
@require_auth
@require_role("admin")
def list_order_route():
    with Session() as session:
        is_admin = g.user['role'] == 'admin'
        return jsonify([o.to_dict() for o in list_orders(session, user_id=g.user['user_id'], is_admin=is_admin)])


@books_bp.route('/orders/<int:oid>/status', methods=['PUT'])
@handle_exceptions
@require_auth
def update_order_route(oid):
    is_admin = g.user['role'] == 'admin'
    user_id = g.user['user_id']
    with Session() as session:
        return jsonify(update_order_status(session, oid, request.json['status'], user_id, is_admin).to_dict())


@books_bp.route('/users')
@handle_exceptions
@require_auth
@require_role("admin")
def list_all_users():
    with Session() as session:
        return jsonify([u.to_dict() for u in list_users(session)])


@books_bp.route('/users', methods=['POST'])
@handle_exceptions
@require_auth
def register_user_route():
    # Check for required fields
    data = request.get_json()
    required_fields = ['username', 'password']
    missing = [f for f in required_fields if not data.get(f)]

    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    with Session() as session:
            return jsonify(register_user(session, request.json).to_dict())
