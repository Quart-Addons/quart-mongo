"""
Tests Odmantic specific connections
using the extension.
"""
import pytest

from quart import Quart
from quart_mongo import Mongo
from quart_mongo.wrappers import AIOEngine

from tests.utils import teardown

from .models import Things

@pytest.mark.asyncio
async def test_odmantic_database_success(uri: str) -> None:
    """
    Tests database successful connection
    for Odmantic.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    assert isinstance(mongo.odm, AIOEngine)
    await teardown(mongo)

@pytest.mark.asyncio
async def test_odmantic_no_database_name_in_uri(client_uri: str) -> None:
    """
    Tests no database name in Mongo URI.
    """
    app = Quart(__name__)
    mongo = Mongo(app, client_uri)
    await app.startup()
    assert mongo.odm is None

@pytest.mark.asyncio
async def test_odmantic_setter(client_uri: str) -> None:
    """
    Tests `Mongo` setter for `Mongo.odm`.
    """
    app = Quart(__name__)
    mongo = Mongo(app, client_uri)
    await app.startup()

    assert mongo.odm is None
    db_name = "test"
    mongo.odm = mongo.cx.odm(db_name)
    assert isinstance(mongo.odm, AIOEngine)
    await teardown(mongo, database=db_name)

@pytest.mark.asyncio
async def test_multiple_odmantic_db_connections(client_uri: str) -> None:
    """
    Tests multiple database connections using Odmantic.
    """
    app = Quart(__name__)
    db1 = Mongo(app, uri=f"{client_uri}test1")
    db2 = Mongo(app, uri=f"{client_uri}test2")
    await app.startup()
    assert isinstance(db1.odm, AIOEngine)
    assert isinstance(db2.odm, AIOEngine)
    await teardown(db1)
    await teardown(db2)

@pytest.mark.asyncio
async def test_odmantic_model(uri: str) -> None:
    """
    Test Odmantic models.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    thing = await mongo.odm.find_one(Things)
    assert thing is None

    thing = Things(id="thing", val="foo")
    await mongo.odm.save(thing)
    thing = await mongo.odm.find_one(Things)
    assert isinstance(thing, Things)
    await teardown(mongo)
