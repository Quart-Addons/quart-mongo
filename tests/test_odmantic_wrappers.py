"""
Tests the wrappers for `Odmantic` provided 
by the extension.
"""
import pytest

from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo import Mongo

from .models import Things
from .utils import teardown

@pytest.mark.asyncio
async def test_odmantic_find_one_or_404_notfound(
    app: Quart, mongo_uri: Mongo) -> None:
    """
    Test not found for `Odmantic.db.find_one_or_404`.
    """
    mongo = mongo_uri
    await app.startup()
    with pytest.raises(NotFound):
        await mongo.odm.find_one_or_404(Things, Things.id == 'thing')
    await teardown(mongo)

@pytest.mark.asyncio
async def test_odmantic_find_one_or_404_found(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Test found for `Odmantic.db.find_one_or_404``.
    """
    mongo = mongo_uri
    await app.startup()
    thing = Things(id="thing", val="foo")
    await mongo.odm.save(thing)
    thing = await mongo.odm.find_one_or_404(Things, Things.id == 'thing')
    assert thing.val == "foo"
    await teardown(mongo)
