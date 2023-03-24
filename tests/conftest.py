"""
Configure pytest.
"""
from typing import AsyncGenerator
import pytest

from quart import Quart
from quart_mongo import Mongo

TEST_DB = "test"
CLIENT_URI = "mongodb://localhost:27017/"
URI = "".join([CLIENT_URI, TEST_DB])


async def _tearDown(mongo: Mongo, database: str | None = None) -> None:
    """
    This function will tear down MongoDB once 
    the tests are completed.
    """
    if database is None:
        if mongo.config.database is not None:
            database = mongo.config.database
        else:
            database = TEST_DB
    await mongo.cx.drop_database(database)

@pytest.fixture
def app() -> Quart:
    """
    Returns the `quart.Quart` application
    used for testing `quart_mongo`.
    """
    app = Quart(__name__)
    return app

@pytest.fixture
async def mongo_uri(app: Quart) -> AsyncGenerator[Mongo, None]:
    """
    Returns an instance of `Mongo` using the uri.
    """
    mongo = Mongo(app, URI)
    yield mongo
    await _tearDown(mongo)

@pytest.fixture
async def mongo_client_uri(app: Quart) -> AsyncGenerator[Mongo, None]:
    """
    Returns an instance of `Mongo` using the client uri
    (no database name provided).
    """
    mongo = Mongo(app, CLIENT_URI)
    yield mongo
    await _tearDown(mongo)

@pytest.fixture
def test_db_name() -> str:
    """
    Returns the test database name.
    """
    return TEST_DB
