"""
tests.odmantic.test_wrappers
"""
import pytest

from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo.odmantic import Odmantic

from .models import Things


@pytest.mark.asyncio
async def test_odmantic_find_one_or_404_notfound(
    db_name: str, uri: str
) -> None:
    """
    Test not found for `Odmantic.engine.find_one_or_404`.
    """
    app = Quart(__name__)
    mongo = Odmantic(app, uri)
    await app.startup()
    assert mongo.cx is not None
    assert mongo.engine is not None
    with pytest.raises(NotFound):
        await mongo.engine.find_one_or_404(Things, Things.id == 'thing')
    await mongo.cx.drop_database(db_name)


@pytest.mark.asyncio
async def test_odmantic_find_one_or_404_found(db_name: str, uri: str) -> None:
    """
    Test found for `Odmantic.engine.find_one_or_404``.
    """
    app = Quart(__name__)
    mongo = Odmantic(app, uri)
    await app.startup()
    assert mongo.cx is not None
    assert mongo.engine is not None
    thing = Things(id="thing", val="foo")
    await mongo.engine.save(thing)
    thing = await mongo.engine.find_one_or_404(
        Things, Things.id == 'thing'
        )
    assert thing.val == "foo"
    await mongo.cx.drop_database(db_name)
