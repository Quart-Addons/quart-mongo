"""
Test the wrappers for `Motor` provided
by the extension.
"""
import pytest

from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo import Mongo

from .utils import teardown

@pytest.mark.asyncio
async def test_motor_find_one_or_404_notfound(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Test not found for `Mongo.db.collection.find_one_or_404`.
    """
    mongo = mongo_uri
    await app.startup()
    with pytest.raises(NotFound):
        await mongo.db.things.find_one_or_404({"id": "thing"})
    await teardown(mongo)

@pytest.mark.asyncio
async def test_motor_find_one_or_404_found(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Test found for `Mongo.db.collection.find_one_or_404`.
    """
    mongo = mongo_uri
    await app.startup()
    await mongo.db.things.insert_one({"_id": "thing", "val": "foo"})
    thing = await mongo.db.things.find_one_or_404({"_id": "thing"})
    assert thing["val"] == "foo"
    await teardown(mongo)
