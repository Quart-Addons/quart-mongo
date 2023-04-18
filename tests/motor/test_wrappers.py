"""
Test the wrappers for `Motor` provided
by the extension.
"""
import pytest

from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo import Mongo

from tests.utils import teardown

@pytest.mark.asyncio
async def test_motor_find_one_or_404_notfound(uri: str) -> None:
    """
    Test not found for `Mongo.db.collection.find_one_or_404`.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    with pytest.raises(NotFound):
        await mongo.db.things.find_one_or_404({"id": "thing"})
    await teardown(mongo)

@pytest.mark.asyncio
async def test_motor_find_one_or_404_found(uri: str) -> None:
    """
    Test found for `Mongo.db.collection.find_one_or_404`.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    await mongo.db.things.insert_one({"_id": "thing", "val": "foo"})
    thing = await mongo.db.things.find_one_or_404({"_id": "thing"})
    assert thing["val"] == "foo"
    await teardown(mongo)
