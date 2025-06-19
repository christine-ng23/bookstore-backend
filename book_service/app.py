### book_service/app.py
from flask import Flask

from common.constants import DB_PATH
from .routes import books_bp

def create_app(db_path):
    # Initializes a Flask application
    app = Flask(__name__)
    # Config for database
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Register a blueprint on the application
    app.register_blueprint(books_bp)
    return app

app = create_app(DB_PATH)
if __name__ == '__main__':
    app.run(port=5001)
