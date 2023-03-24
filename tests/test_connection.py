"""
Test general connections to the database.
"""
from typing import Generator
import pytest

from pymongo.errors import InvalidURI
from quart import Quart
from quart_mongo import Mongo

from .utils import CouldNotConnect, wait_until_connected

@pytest.mark.asyncio
async def test_client_connection(mongo_client_uri) -> None:
    """
    Test client connection to the database.
    """
    async with mongo_client_uri as mongo:
        assert isinstance(mongo, Mongo)

def test_invaild_uri(app) -> None:
    """
    Test an invalid Mongo uri.
    """
    with pytest.raises(InvalidURI):
        Mongo(app, uri="http://localhost:27017/test")

def test_database_failure(app) -> None:
    """
    Test database connection failure when no URI is provided
    directly to the `quart_mongo.Mongo` class or to the app
    config.
    """
    with pytest.raises(ValueError):
        Mongo(app)

@pytest.mark.asyncio
async def test_doesnt_connect_by_default(
    app: Quart, mongo_uri: Generator[Mongo]
    ) -> None:
    """
    Test that the database doesn't connect by default.
    """
    async with mongo_uri as mongo:
        await app.startup()
        with pytest.raises(CouldNotConnect):
            wait_until_connected(mongo, timeout=0.2)
