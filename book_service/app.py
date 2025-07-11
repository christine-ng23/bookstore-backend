### book_service/app.py
from flask import Flask
from flask_cors import CORS

from auth_service.config import FRONTEND_SERVER
from book_service.reset_route import reset_blueprint
from common.config import DB_PATH
from .routes import books_bp
from .auth_proxy import auth_proxy_bp

def create_app(session_factory=None):
    # Initializes a Flask application
    app = Flask(__name__)
    # Config for database factory to support testing
    app.config["SESSION_FACTORY"] = session_factory
    # Default config for database
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Enable CORS
    CORS(app,
         supports_credentials=True,  # allow sending cookies or Authorization header
         origins=[f"{FRONTEND_SERVER}"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    # Register a blueprint on the application
    app.register_blueprint(books_bp)
    app.register_blueprint(auth_proxy_bp)
    app.register_blueprint(reset_blueprint)
    return app

app = create_app()
if __name__ == '__main__':
    app.run(port=5001)
