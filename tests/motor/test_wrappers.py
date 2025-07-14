"""
tests.motor.test_wrappers
"""
import pytest

from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo import Motor


@pytest.mark.asyncio
async def test_motor_find_one_or_404_notfound(app: Quart, uri: str) -> None:
    """
    Test not found for `Mongo.db.collection.find_one_or_404`.
    """
    mongo = Motor(app, uri)
    await app.startup()
    assert mongo.db is not None
    with pytest.raises(NotFound):
        await mongo.db.things.find_one_or_404({"id": "thing"})


@pytest.mark.asyncio
async def test_motor_find_one_or_404_found(app: Quart, uri: str) -> None:
    """
    Test found for `Mongo.db.collection.find_one_or_404`.
    """
    mongo = Motor(app, uri)
    await app.startup()
    assert mongo.db is not None
    await mongo.db.things.insert_one({"_id": "thing", "val": "foo"})
    thing = await mongo.db.things.find_one_or_404({"_id": "thing"})
    assert thing["val"] == "foo"
