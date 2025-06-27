## common/constants.py

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'bookstore.db')
TEST_DATA_DIR = os.path.join(BASE_DIR, 'tests', 'data')
DEFAULT_TEST_SEED_JSON = "test_seed.json"
TEST_SESSION_TYPE = "in_memory"   # "in_memory" or "real" Using in for api and service-model integration test

# User Roles
class Roles:
    USER = "user"
    ADMIN = "admin"
    ALL = {USER, ADMIN}

# Order Statuses
class OrderStatus:
    NEW = 'new'
    PROCESSING = 'processing'
    SHIPPING = 'shipping'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'
    REJECTED = 'rejected'

    ALL = {NEW, PROCESSING, SHIPPING, DELIVERED, CANCELED, REJECTED}

# Order Status Transition Map
ORDER_TRANSITIONS = {
    OrderStatus.NEW: [OrderStatus.PROCESSING, OrderStatus.CANCELED, OrderStatus.REJECTED],
    OrderStatus.PROCESSING: [OrderStatus.SHIPPING, OrderStatus.REJECTED],
    OrderStatus.SHIPPING: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELED: [],
    OrderStatus.REJECTED: [],
}
