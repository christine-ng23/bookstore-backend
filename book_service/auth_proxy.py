## book_service/auth_proxy.py
"""
Proxy to auth server, for example to exchange code with access token
"""
from flask import Blueprint, request, jsonify
import requests

from auth_service.config import CLIENT_ID, CLIENT_SECRET, AUTH_SERVER
from book_service.utils.utils import validate_field_types

auth_proxy_bp = Blueprint("auth_proxy", __name__)

@auth_proxy_bp.route("/auth/token", methods=["POST"])
def exchange_code():
    """
    POST /auth/token

    Proxy to auth server to get an access token

    Requirements:
    - Required fields: code
    - Field types: "code": str
    - code must be valid

    Response:
    - 200: Return an access token (proxy form Auth endpoint)
    - 400: Validation errors on required fields, fields types
    - 401: Invalid client or code (proxy form Auth endpoint)
    - 500: Server error
    """
    data = request.get_json()
    code = data.get("code")

    # Validate required field
    if not code:
        return jsonify({"error": "Missing required field: code"}), 400

    # Validate field type
    errors = []
    validate_field_types(data, {"code": str}, errors)
    if errors:
        return {"error": "; ".join(errors)}, 400
    try:
        response = requests.post(f"{AUTH_SERVER}/token", json={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        })
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": f"Failed to get access token: {str(e)}"}), 500
