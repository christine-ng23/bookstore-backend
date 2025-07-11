## book_service/reset_route.py
"""
Provide APIs for loading test data
"""
from flask import Blueprint, request, jsonify, current_app
from auth_service.db import get_session
from common.config import RUNNING_ENV, ENV, TEST_SECRET_KEY
from test_utils.data_loader import clean_data, initialize_data
from werkzeug.utils import secure_filename
from io import BytesIO
import json

reset_blueprint = Blueprint('reset', __name__)

@reset_blueprint.route('/test/reset_and_load', methods=['POST'])
def reset_and_load():
    if RUNNING_ENV != ENV.TEST:
        return jsonify({"error": "Forbidden"}), 403

    auth_header = request.headers.get("X-Test-Secret")
    if auth_header != TEST_SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Check for raw JSON body
        if request.is_json:
            data = request.get_json()
        # Check for uploaded JSON file
        elif 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)

            if not filename.endswith('.json'):
                return jsonify({"error": "Uploaded file must be a .json file"}), 400

            data = json.load(BytesIO(file.read()))
        else:
            return jsonify({"error": "Must upload JSON file or send JSON body"}), 400

        session = get_session()
        clean_data(session)
        initialize_data(session, data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500