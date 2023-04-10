"""
Test general connections to the database.
"""
import pytest

from pymongo.errors import InvalidURI
from quart import Quart
from quart_mongo import Mongo

from .utils import CouldNotConnect, wait_until_connected

@pytest.mark.asyncio
async def test_client_connection(mongo_client_uri: Mongo):
    """
    Test client connection to the database.
    """
    mongo = mongo_client_uri
    assert isinstance(mongo, Mongo)

def test_invalid_uri(app: Quart) -> None:
    """
    Test an invalid Mongo URI.
    """
    with pytest.raises(InvalidURI):
        Mongo(app, "http://localhost:27017/test")

def test_database_failure(app: Quart) -> None:
    """
    Test database connection failure when no URI
    is provided directly to the class or app config.
    """
    with pytest.raises(ValueError):
        Mongo(app)

@pytest.mark.asyncio
async def test_doesnt_connect_by_default(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Test that the database doesn't connect
    by default.
    """
    mongo = mongo_uri
    await app.startup()

    with pytest.raises(CouldNotConnect):
        wait_until_connected(mongo, 0.2)
