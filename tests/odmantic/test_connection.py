"""
tests.odmantic.test_connection
"""
import pytest

from quart import Quart
from quart_mongo.odmantic import Odmantic
from quart_mongo.odmantic.wrappers import AIOEngine

from .models import Things


@pytest.mark.asyncio
async def test_odmantic_database_success(db_name: str, uri: str) -> None:
    """
    Tests database successful connection
    for Odmantic.
    """
    app = Quart(__name__)
    mongo = Odmantic(app, uri)
    await app.startup()
    assert mongo.cx is not None
    assert isinstance(mongo.engine, AIOEngine)
    await mongo.cx.drop_database(db_name)


@pytest.mark.asyncio
async def test_odmantic_no_database_name_in_uri(client_uri: str) -> None:
    """
    Tests no database name in Mongo URI.
    """
    app = Quart(__name__)
    mongo = Odmantic(app, client_uri)
    await app.startup()
    assert mongo.engine is None


@pytest.mark.asyncio
async def test_odmantic_setter(client_uri: str) -> None:
    """
    Tests `Mongo` setter for `Mongo.odm`.
    """
    app = Quart(__name__)
    mongo = Odmantic(app, client_uri)
    await app.startup()

    assert mongo.cx is not None
    assert mongo.engine is None
    db_name = "test"
    mongo.engine = AIOEngine(client=mongo.cx, database=db_name)
    assert isinstance(mongo.engine, AIOEngine)
    await mongo.cx.drop_database(db_name)


@pytest.mark.asyncio
async def test_multiple_odmantic_db_connections(client_uri: str) -> None:
    """
    Tests multiple database connections using Odmantic.
    """
    app = Quart(__name__)
    db1 = Odmantic(app, uri=f"{client_uri}test1")
    db2 = Odmantic(app, uri=f"{client_uri}test2")
    await app.startup()
    assert db1.cx is not None
    assert db2.cx is not None
    assert isinstance(db1.engine, AIOEngine)
    assert isinstance(db2.engine, AIOEngine)
    await db1.cx.drop_database("test1")
    await db2.cx.drop_database("test2")


@pytest.mark.asyncio
async def test_odmantic_model(db_name: str, uri: str) -> None:
    """
    Test Odmantic models.
    """
    app = Quart(__name__)
    mongo = Odmantic(app, uri)
    await app.startup()
    assert mongo.cx is not None
    assert mongo.engine is not None
    thing = await mongo.engine.find_one(Things)
    assert thing is None

    thing = Things(id="thing", val="foo")
    await mongo.engine.save(thing)
    thing = await mongo.engine.find_one(Things)
    assert isinstance(thing, Things)
    await mongo.cx.drop_database(db_name)
