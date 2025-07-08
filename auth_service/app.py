## auth_service/app.py
from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from auth_service.config import FRONTEND_SERVER
from .routes import auth_api_ns

def create_app(session_factory=None):
    app = Flask(__name__)
    app.config["SESSION_FACTORY"] = session_factory
    # Enable CORS
    CORS(app,
         supports_credentials=True,  # allow sending cookies or Authorization header
         origins=[f"{FRONTEND_SERVER}"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    # Register Swagger API
    api = Api(
        app,
        title="Auth Service API",
        version="1.0",
        description="Authentication and Token APIs",
        doc="/"  # Swagger UI at root
    )
    api.add_namespace(auth_api_ns)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5000)
