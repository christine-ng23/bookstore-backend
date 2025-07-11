## tests/book_service/conftest.py

import pytest

from book_service.app import create_app
from test_utils.data_loader import initialize_data_from_json
from tests.utils.session_factory import session_factory


@pytest.fixture
def mock_session(request):
    # Notes: mock_session don't support validate fields and relationships
    class MockQuery:
        def __init__(self, data):
            self.data = data
            self._filter = {}

        def filter_by(self, **kwargs):
            self._filter = kwargs
            return self

        def filter(self, *args):
            # Simulate something like Book.id == 1
            for expr in args:
                try:
                    key = expr.left.name
                    value = expr.right.value
                    self._filter[key] = value
                except AttributeError:
                    pass
            return self

        def first(self):
            for obj in self.data.values():
                if all(getattr(obj, k) == v for k, v in self._filter.items()):
                    return obj
            return None

        def all(self):
            return list(self.data.values())

    class MockSession:
        def __init__(self):
            self.data = {}
            self.ids = {}

        def query(self, model):
            if model.__name__ in self.data:
                return MockQuery(self.data[model.__name__])
            else:
                return MockQuery({})

        def add(self, obj):
            table = obj.__class__.__name__
            if table in self.data:
                obj.id = self.ids[table] + 1
                self.data[table][obj.id] = obj
            else:
                self.ids[table] = 1
                obj.id = 1
                self.data[table] = {obj.id: obj}

        def flush(self):
            pass

        def commit(self):
            pass

        def delete(self, obj):
            table = obj.__class__.__name__

            if obj.id in self.data[table]:
                del self.data[table][obj.id]

        def close(self):
            self.data = {}

    param = getattr(request, "param", {})
    json_file = param.get("json_file", None)
    # Preload data if specified
    session = MockSession()
    if json_file:
        initialize_data_from_json(session, json_file)
    yield session
    session.close()


@pytest.fixture
def db_session(request):  # in memory db session
    param = getattr(request, "param", {})
    session_type = param.get("type", "in_memory")
    json_file = param.get("json_file", None)
    Session = session_factory(session_type=session_type, json_file=json_file)
    session = Session()

    yield session

    # Clean all tables
    session.close()


@pytest.fixture
def client(request):  # Client with default in memory db session and no data initialization
    param = getattr(request, "param", {})
    session_type = param.get("type", "in_memory")
    json_file = param.get("json_file", None)

    factory = session_factory(session_type=session_type, json_file=json_file)
    app = create_app(session_factory=factory)

    with app.test_client() as _client:
        yield _client

