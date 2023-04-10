"""
Tests `Motor` specific connections using the extension.
"""
import pytest
from quart import Quart
from quart_mongo import Mongo
from quart_mongo.wrappers import AIOMotorDatabase

from .utils import teardown

@pytest.mark.asyncio
async def test_motor_database_success(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Tests database successful connection.
    """
    mongo = mongo_uri
    await app.startup()
    assert isinstance(mongo.db, AIOMotorDatabase)
    await teardown(Mongo)

@pytest.mark.asyncio
async def test_multiple_motor_connections(
    app: Quart, client_uri: Mongo
    ) -> None:
    """
    Tests multiple database connections.
    """
    db1 = Mongo(app, uri=f"{client_uri}test1")
    db2 = Mongo(app, uri=f"{client_uri}test2")
    await app.startup()
    assert isinstance(db1.db, AIOMotorDatabase)
    assert isinstance(db2.db, AIOMotorDatabase)
    await teardown(db1)
    await teardown(db2)

@pytest.mark.asyncio
async def test_motor_no_database_name_in_uri(
    app: Quart, mongo_client_uri: Mongo
    ) -> None:
    """
    Test no database name in URI.
    """
    mongo =  mongo_client_uri
    await app.startup()
    assert mongo.db is None

@pytest.mark.asyncio
async def test_motor_custom_class(
    app: Quart, uri: str
    ) -> None:
    """
    Test custom document class.
    """
    class CustomDict(dict):
        """
        Custom document class.
        """

    mongo = Mongo(app, uri, document_class = CustomDict)
    await app.startup()
    things = await mongo.db.things.find_one()
    assert things is None

    await mongo.db.things.insert_one({"_id": "thing", "val": "foo"})
    things = await mongo.db.things.find_one()
    assert isinstance(things, CustomDict)
    await teardown(mongo)
