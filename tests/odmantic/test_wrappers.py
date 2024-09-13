"""
tests.odmantic.test_wrapper
"""
import pytest

from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo import Mongo

from tests.utils import teardown

from .models import Things


@pytest.mark.asyncio
async def test_odmantic_find_one_or_404_notfound(uri: str) -> None:
    """
    Test not found for `Odmantic.db.find_one_or_404`.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    with pytest.raises(NotFound):
        await mongo.odm.find_one_or_404(Things, Things.id == 'thing')
    await teardown(mongo)


@pytest.mark.asyncio
async def test_odmantic_find_one_or_404_found(uri: str) -> None:
    """
    Test found for `Odmantic.db.find_one_or_404``.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    thing = Things(id="thing", val="foo")
    await mongo.odm.save(thing)
    thing: Things = await mongo.odm.find_one_or_404(
        Things, Things.id == 'thing'
        )
    assert thing.val == "foo"
    await teardown(mongo)
