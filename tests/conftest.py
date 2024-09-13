"""
tests.conftest
"""
import pytest


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
