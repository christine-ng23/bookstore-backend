# common/config.py
import os

from dotenv import load_dotenv

# ENV constants
class ENV:
    TEST = 'test'
    PRODUCTION = 'production'

# Read from environment variable
load_dotenv()
RUNNING_ENV = os.environ.get('ENV', ENV.TEST)

# DB paths for each env
DBS = {
    ENV.TEST: 'test.db',
    ENV.PRODUCTION: 'bookstore.db'
}

if RUNNING_ENV not in DBS:
    raise ValueError(f"Invalid ENV: {RUNNING_ENV}")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_NAME = DBS[RUNNING_ENV]
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

# Secret key for test API
TEST_SECRET_KEY = "super-secret"

# For test setup
TEST_DATA_DIR = os.path.join(BASE_DIR, 'tests', 'data')
TEST_SESSION_TYPE = "in_memory"  # in_memory or "real"
