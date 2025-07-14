"""
tests.odmantic.quart_schema.conftest
"""
import pytest

from quart import Quart
from quart_schema import QuartSchema
from quart_mongo.odmantic import Odmantic


@pytest.fixture
async def app(db_name: str, uri: str):
    """
    App for test Quart Schema with Odmantic.
    """
    test_app = Quart(__name__)

    config = {
        "MONGO_URI": uri
    }

    test_app.config.from_mapping(config)

    QuartSchema(test_app)
    mongo = Odmantic(test_app, uri)
    test_app.extensions["odmantic"] = mongo

    await test_app.startup()

    yield test_app

    if mongo.cx is not None:
        await mongo.cx.drop_database(db_name)

    await test_app.shutdown()
