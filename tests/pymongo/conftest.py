"""
tests.pymongo.conftest
"""
from typing import Any, AsyncGenerator

import pytest
from quart import Quart
from quart_mongo.pymongo.wrappers import MongoClient


@pytest.fixture
async def test_app(
    port: int, db_name: str, uri: str
) -> AsyncGenerator[Quart, None]:
    """
    `quart.Quart` app for testing.
    """
    conn: MongoClient[Any] = MongoClient(port=port)
    await conn.test.command("ping")  # wait for server
    await conn.close()

    app = Quart(__name__)

    config = {
        "MONGO_URI": uri
    }

    app.config.from_mapping(config)

    await app.startup()

    yield app

    # teardown MongoDB
    client: MongoClient[Any] = MongoClient(port=port)
    await client.drop_database(db_name)
    await client.close()

    await app.shutdown()
