"""
tests.motor.conftest
"""
from typing import AsyncGenerator

import pytest
from quart import Quart
from quart_mongo.motor.wrappers import AsyncIOMotorClient


@pytest.fixture
async def app(
    port: int, db_name: str, uri: str
) -> AsyncGenerator[Quart, None]:
    """
    `quart.Quart` app for testing.
    """
    conn: AsyncIOMotorClient = AsyncIOMotorClient(port=port)
    await conn.test.command("ping")  # wait for server
    conn.close()

    app = Quart(__name__)

    config = {
        "MONGO_URI": uri
    }

    app.config.from_mapping(config)

    yield app

    # teardown MongoDB
    client: AsyncIOMotorClient = AsyncIOMotorClient(port=port)
    await client.drop_database(db_name)
    client.close()

    await app.shutdown()
