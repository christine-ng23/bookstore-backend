### auth_service/app.py
from flask import Flask

from auth_service.config import SECRET
from .routes import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(port=5000)
