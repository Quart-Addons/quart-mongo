"""
tests.test_general_connection
"""
import pytest

from pymongo.errors import InvalidURI
from quart import Quart
from quart_mongo import Mongo

from .utils import CouldNotConnect, wait_until_connected


@pytest.mark.asyncio
async def test_client_connection(client_uri: str) -> None:
    """
    Test client connection to the database.
    """
    app = Quart(__name__)
    mongo = Mongo(app, client_uri)
    assert isinstance(mongo, Mongo)


def test_invalid_uri() -> None:
    """
    Test an invalid Mongo URI.
    """
    app = Quart(__name__)
    with pytest.raises(InvalidURI):
        Mongo(app, "http://localhost:27017/test")


def test_database_failure() -> None:
    """
    Test database connection failure when no URI
    is provided directly to the class or app config.
    """
    app = Quart(__name__)
    with pytest.raises(ValueError):
        Mongo(app)


@pytest.mark.asyncio
async def test_doesnt_connect_by_default(uri: str) -> None:
    """
    Test that the database doesn't connect
    by default.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()

    with pytest.raises(CouldNotConnect):
        wait_until_connected(mongo, 0.2)
