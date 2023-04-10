"""
Pytest Configuration. 
"""
import pytest

from quart import Quart
from quart_mongo import Mongo

@pytest.fixture
def app() -> Quart:
    """
    Returns a `quart.Quart` application
    to use for testing.
    """
    app = Quart(__name__)
    return app

@pytest.fixture
def uri() -> str:
    """
    Returns the uri for Mongo.
    """
    return "mongodb://localhost:27017/test"

@pytest.fixture
def client_uri() -> str:
    """
    Returns for the client uri for Mongo.
    """
    return "mongodb://localhost:27017/"

@pytest.fixture
def mongo_uri(app: Quart, uri: str) -> Mongo:
    """
    Returns an instance of `Mongo` using a uri.
    """
    return Mongo(app, uri)

@pytest.fixture
def mongo_client_uri(app: Quart, client_uri: str) -> Mongo:
    """
    Returns an instance of `Mongo` using the client uri.
    """
    return Mongo(app, client_uri)
