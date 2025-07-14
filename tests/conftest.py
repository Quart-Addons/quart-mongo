"""
tests.conftest
"""
import pytest


@pytest.fixture
def port() -> int:
    """
    MongoDB Port
    """
    return 27017


@pytest.fixture
def client_uri(port: int) -> str:
    """
    MongoDB Client URI
    """
    return f"mongodb://localhost:{str(port)}/"


@pytest.fixture
def db_name() -> str:
    """
    Database name.
    """
    return "test"


@pytest.fixture
def uri(client_uri: str, db_name: str) -> str:
    """
    Returns the uri for Mongo.
    """
    return client_uri + db_name
