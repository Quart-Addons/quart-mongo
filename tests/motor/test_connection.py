"""
tests.motor.test_connection
"""
import pytest
from quart import Quart
from quart_mongo import Motor
from quart_mongo.motor.wrappers import AsyncIOMotorDatabase


@pytest.mark.asyncio
async def test_motor_database_success(db_name: str, uri: str) -> None:
    """
    Tests database successful connection.
    """
    app = Quart(__name__)
    mongo = Motor(app, uri)
    await app.startup()
    assert isinstance(mongo.db, AsyncIOMotorDatabase)
    await mongo.cx.drop_database(db_name)


@pytest.mark.asyncio
async def test_multiple_motor_connections(client_uri: str) -> None:
    """
    Tests multiple database connections.
    """
    app = Quart(__name__)
    db1 = Motor(app, uri=f"{client_uri}test1")
    db2 = Motor(app, uri=f"{client_uri}test2")
    await app.startup()
    assert isinstance(db1.db, AsyncIOMotorDatabase)
    assert isinstance(db2.db, AsyncIOMotorDatabase)
    await db1.cx.drop_database("test1")
    await db2.cx.drop_database("test2")


@pytest.mark.asyncio
async def test_motor_no_database_name_in_uri(client_uri: str) -> None:
    """
    Test no database name in URI.
    """
    app = Quart(__name__)
    mongo = Motor(app, client_uri)
    await app.startup()
    assert mongo.db is None


@pytest.mark.asyncio
async def test_motor_custom_class(app: Quart, uri: str) -> None:
    """
    Test custom document class.
    """
    class CustomDict(dict):
        """
        Custom document class.
        """
    mongo = Motor(app, uri, document_class=CustomDict)
    await app.startup()
    assert mongo.db is not None
    things = await mongo.db.things.find_one()
    assert things is None

    await mongo.db.things.insert_one({"_id": "thing", "val": "foo"})
    things = await mongo.db.things.find_one()
    assert isinstance(things, CustomDict)
