"""
tests.pymongo.test_config
"""
from typing import Any

import pytest
from quart import Quart
from quart_mongo import PyMongo
from quart_mongo.pymongo.wrappers import Database


@pytest.mark.asyncio
async def test_config_with_uri_in_quart_config(
    port: str, db_name: str, test_app: Quart
) -> None:
    """
    Test that Mongo uri is in `quart.Quart` config.
    """
    mongo = PyMongo(test_app, connect=True)

    assert mongo.cx is not None
    assert mongo.db is not None
    assert mongo.db.name == db_name
    assert ("localhost", port) == await mongo.cx.address

    await mongo.cx.close()


@pytest.mark.asyncio
async def test_config_uri_passed_directly(
    port: str, db_name: str, uri: str, test_app: Quart
) -> None:
    """
    Test passing the uri directly to `quart_mongo.Mongo`.
    """
    mongo = PyMongo(test_app, uri, connect=True)

    assert mongo.cx is not None
    assert mongo.db is not None
    assert mongo.db.name == db_name
    assert ("localhost", port) == await mongo.cx.address

    await mongo.cx.close()


def test_fails_with_no_uri(test_app: Quart) -> None:
    """
    Test that `quart_mongo.Mongo` raises
    ``ValueError`` when no uri is provided.
    """
    test_app.config.pop("MONGO_URI", None)

    with pytest.raises(ValueError):
        PyMongo(test_app)


def test_multiple_instances(
        client_uri: str, test_app: Quart
) -> None:
    """
    Test multiple instances of `quart_mongo.Mongo`.
    """
    uri1 = client_uri + "test1"
    uri2 = client_uri + "test2"

    mongo1 = PyMongo(test_app, uri1)
    mongo2 = PyMongo(test_app, uri2)

    assert isinstance(mongo1.db, Database)
    assert isinstance(mongo2.db, Database)


@pytest.mark.asyncio
async def test_custom_document_class(
    uri: str, test_app: Quart
) -> None:
    """
    Test custom document class with pymongo
    """
    class CustomDict(dict[str, Any]):
        """
        Custom Dict
        """

    mongo = PyMongo(test_app, uri, document_class=CustomDict)

    assert mongo.cx is not None
    assert mongo.db is not None
    assert await mongo.db.things.find_one() is None, "precondition failed"

    await mongo.db.things.insert_one({"_id": "thing", "val": "foo"})

    value = await mongo.db.things.find_one()
    assert isinstance(value, CustomDict)

    await mongo.cx.close()
