Project: Demo for a Bookstore Web App (Microservice Architecture) with OAuth2 Authorization

## Folder Structure:

```
bookstore-app/
├── README.md
├── frontend/
├── admin_portal/
├── common/
│   ├── models.py              # Shared User model and Base
│   └── constants.py           # Shared config (DB_PATH) (Current version services use shared db)
├── auth_service/              # OAuth2 authorization service
│   ├── app.py
│   ├── routes.py
│   ├── auth_middleware.py
│   ├── token_utils.py
│   ├── db.py
│   ├── config.py              # Auth config (SECRET, TOKEN_EXPIRE_MINUTES)
│   ├── init_admin.py
│   └── tests/
│       ├── unit/
│       │   └── test_jwt_util.py
│       ├── itegration
│       │   └── test_auth_decorators.py
│       └── api
│           └── test_route.py
├── book_service/              # Book microservice
│   ├── app.py
│   ├── models.py              # SQLAlchemy models
│   ├── db.py                  # Database setup
│   ├── routes.py
│   ├── services/              # Book, Order, User logic
│   │   ├── book_service.py
│   │   ├── order_service.py
│   │   └── user_service.py
│   └── tests/
│       ├── unit/
│       │   ├── conftest.py
│       │   ├── test_book_model.py
│       │   ├── test_user_model.py
│       │   ├── test_order_model.py
│       │   └── test_order_item_model.py
│       ├── itegration
│       │   ├── test_book_service.py
│       │   ├── test_order_service.py
│       │   └── test_user_service.py
│       └── api
│           └── test_route.py
├── bookstore.db              # SQLite database file
├── docker-compose.yml
└── requirements.txt

```

## Description:
A microservice-based bookstore web application with two portals:
- **Customer Portal (React)** for book browsing and orders
- **Admin Portal (React)** for user, book, and order management
- **Auth Service (Flask)** handles OAuth2 token issuance
- **Book Service (Flask)** persists data in SQLite using SQLAlchemy

## Technologies:
- Frontend: React, axios
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

# Run auth service
cd auth_service && flask run --port 5000

# Run frontend portals
cd frontend && npm install && npm start
cd admin_portal && npm install && npm start
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
pytest auth_service/tests/
pytest book_service/tests/
python integration_test.py
```

## Security Considerations:
- Use HTTPS in production
- JWT-based auth, scoped by roles
- Avoid hardcoded secrets in production (use env vars)

## License:
MIT

