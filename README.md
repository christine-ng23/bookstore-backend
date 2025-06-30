Project: Demo for a Bookstore Web App Backend (Microservice Architecture) with OAuth2 Authorization

## Folder Structure:

```
bookstore-app/
├── README.md
├── requirements.txt
├── bookstore.db
├── auth_service/
│    ├── __init__.py
│    ├── app.py                    # Create, config, run app (Werkzeug's WSGI server)
│    ├── auth_middleware.py        # OAuth2 authorization service
│    ├── config.py                 # Auth config (SECRET, TOKEN_EXPIRE_MINUTES)
│    ├── db.py
│    ├── init_admin.py
│    ├── routes.py
│    └── token_utils.py
├── book_service/
│    ├── __init__.py
│    ├── app.py                    # Create, config, run app (Werkzeug's WSGI server)
│    ├── db.py
│    ├── models.py
│    ├── routes.py
│    ├── services/
│    │    ├── __init__.py
│    │    ├── book_service.py
│    │    ├── order_service.py
│    │    └── user_service.py
│    └── utils/
│        ├── __init__.py
│        ├── handlers.py           # Decorator (handle exception at api level)
│        └── utils.py
├── common/
│    ├── __init__.py
│    ├── auth.py                   # Commom auth utils
│    ├── constants.py              # Shared config (DB_PATH)
│    ├── exceptions.py             # Custom exception
│    └── models.py                 # Shared User model and Base
└── tests/
    ├── __init__.py
    ├── auth_service/                   
    │    ├── __init__.py
    │    ├── api/
    │    │    ├── __init__.py
    │    │    ├── pages/
    │    │    │    ├── __init__.py
    │    │    │    └── auth_api.py
    │    │    └── test_auth_endpoints.py
    │    ├── conftest.py
    │    ├── integration/
    │    │    ├── __init__.py
    │    │    └── test_auth_decorators.py    # Auth decorators
    │    └── unit/
    │         ├── __init__.py
    │         └── test_jwt_util.py
    ├── book_service/
    │    ├── __init__.py
    │    ├── api/
    │    │    ├── __init__.py
    │    │    ├── test_book_api.py
    │    │    ├── test_order_api.py
    │    │    └── test_user_api.py
    │    ├── conftest.py
    │    ├── integration/
    │    │    ├── __init__.py
    │    │    └── test_user_service.py
    │    └── unit/
    │         ├── __init__.py
    │         ├── test_book_model.py
    │         ├── test_order_item_model.py
    │         ├── test_order_model.py
    │         ├── test_user_model.py
    │         └── test_user_service_isolated.py
    ├── conftest.py
    ├── data/
    │    ├── __init__.py
    │    ├── test_data.json
    │    ├── test_seed.json
    │    ├── test_seed_only_users.json
    │    └── test_seed_users_books.json
    └── utils/
         ├── __init__.py
         ├── data_loader.py
         ├── session_factory.py
         └── validator.py

```

## Description:
A microservice-based bookstore web application backend:
- **Auth Service (Flask)** handles OAuth2 token issuance
- **Book Service (Flask)** persists data in SQLite using SQLAlchemy

The frontend will reside in a separate repository (future development)
- **Customer Portal (React)** for book browsing and orders
- **Admin Portal (React)** for user, book, and order management

## Technologies:
- Backend: Flask, SQLAlchemy, pyjwt, requests, pytest
- Auth: OAuth 2.0 Authorization Code Grant
- DB: SQLite (bookstore.db)

## Setup:
```bash
# Install backend dependencies
pip install -r requirements.txt

# Initialize database schema
python -m auth_service.db  # Creates tables using common/models.py
python -m auth_service.init_admin  # Add default admin user
python -m book_service.db  # Creates tables using models.py

cd book_service && flask run --port 5001

# Run auth service and swagger documentation ready at http://127.0.0.1:5000/
cd auth_service && flask run --port 5000
```

## Auth Roles:
- Admin: manage users, books, orders (view/add/edit/delete/status update)
- Customer: register, login, browse/search books, make orders, cancel new orders

## Backend Features:
- **Books**: CRUD (admin), list/search (all)
- **Users**: register (customer), list/view/add/edit/delete (admin)
- **Orders**: place/view (customer), update status (admin), cancel new (customer)

## Database:
SQLite used for persistence.
- **users**: id, username, password, role
- **books**: id, code, name, publisher, quantity, imported_price, sell_price
- **orders**: id, user_id, status, created_at
- **order_items**: id, order_id, book_id, quantity, price_each
- Managed with SQLAlchemy ORM in `models.py`

## Endpoints:

### Auth Service
- `GET /authorize` | `POST /token`

### Book Service (JWT-secured)
- `GET /books`, `GET /books/<id>`
- `POST /books`, `PUT /books/<id>`, `DELETE /books/<id>` (admin)
- `GET /users`, `POST /users`, `PUT /users/<id>`, `DELETE /users/<id>` (admin)
- `POST /register` (customer)
- `POST /orders`, `GET /orders`, `PUT /orders/<id>/status`

## Testing:
```bash
# Running all test
pytest tests/
# Running test with code coverage measurement
pytest --cov=book_service --cov=auth_service --cov=common --cov-report=term-missing
# With HTML report (report goes into folder: htmlcov)
pytest tests/**/unit/ --cov=book_service --cov=auth_service --cov=common --cov-report=html
# Check coverage for specific file
pytest --cov=book_service/services/books.py --cov-report=term-missing

```
Explanation:
- --cov=module_name: track coverage for that package/module (repeat for each)
- --cov-report=term-missing: shows which lines weren't executed

Output would look like:
```
book_service/services/book_service.py       85%   lines 33-35 not covered
auth_service/routes.py            100%
common/models.py             90%   line 19 not covered
```

## Security Considerations:
- Use HTTPS in production
- JWT-based auth, scoped by roles
- Avoid hardcoded secrets in production (use env vars)

## License:
MIT

