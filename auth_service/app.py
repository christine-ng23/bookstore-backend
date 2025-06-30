## auth_service/app.py
from flask import Flask
from flask_restx import Api

from .routes import auth_api_ns

def create_app(session_factory=None):
    app = Flask(__name__)
    app.config["SESSION_FACTORY"] = session_factory

    # Register Swagger API
    # Register Flask-RESTX API
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
