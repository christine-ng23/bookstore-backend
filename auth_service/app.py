## auth_service/app.py
from flask import Flask

from .routes import auth_bp


def create_app(session_factory=None):
    app = Flask(__name__)
    app.config["SESSION_FACTORY"] = session_factory
    app.register_blueprint(auth_bp)
    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5000)
