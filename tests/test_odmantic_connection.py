"""
Tests Odmantic specific connections
using the extension.
"""
import pytest

from quart import Quart
from quart_mongo import Mongo
from quart_mongo.wrappers import AIOEngine

from .models import Things
from .utils import teardown

@pytest.mark.asyncio
async def test_odmantic_database_success(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Tests database successful connection
    for Odmantic.
    """
    mongo = mongo_uri
    await app.startup()
    assert isinstance(mongo.odm, AIOEngine)
    await teardown(mongo)

@pytest.mark.asyncio
async def test_odmantic_no_database_name_in_uri(
    app: Quart, mongo_client_uri: Mongo
    ) -> None:
    """
    Tests no database name in Mongo URI.
    """
    mongo = mongo_client_uri
    await app.startup()
    assert mongo.odm is None

@pytest.mark.asyncio
async def test_odmantic_setter(
    app: Quart, mongo_client_uri: Mongo
    ) -> None:
    """
    Tests `Mongo` setter for `Mongo.odm`.
    """
    db_name = "test"
    mongo = mongo_client_uri
    await app.startup()

    assert mongo.odm is None
    mongo.odm = mongo.cx.odm(db_name)
    assert isinstance(mongo.odm, AIOEngine)
    await teardown(mongo, database=db_name)

@pytest.mark.asyncio
async def test_multiple_odmantic_db_connections(
    app: Quart, client_uri: Mongo
    ) -> None:
    """
    Tests multiple database connections using Odmantic.
    """
    db1 = Mongo(app, uri=f"{client_uri}test1")
    db2 = Mongo(app, uri=f"{client_uri}test2")
    await app.startup()
    assert isinstance(db1.odm, AIOEngine)
    assert isinstance(db2.odm, AIOEngine)
    await teardown(db1)
    await teardown(db2)
