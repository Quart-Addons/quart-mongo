"""
tests.pymongo.wrappers
"""
from typing import Any, Dict

import pytest
from quart import Quart
from werkzeug.exceptions import HTTPException

from quart_mongo import PyMongo


@pytest.fixture
def mongo(test_app: Quart) -> PyMongo:
    """
    Instance of `quart_mongo.Mongo`
    used for test
    """
    db = PyMongo(test_app)
    return db


@pytest.mark.asyncio
async def test_find_one_or_404(mongo: PyMongo) -> None:
    """
    Test find or 404 from pymongo wrapper
    """
    assert mongo.db is not None
    await mongo.db.things.delete_many({})

    try:
        await mongo.db.things.find_one_or_404({"_id": "thing"})
    except HTTPException as notfound:
        assert notfound.code == 404, "raised wrong exception"

    await mongo.db.things.insert_one({"_id": "thing", "val": "foo"})

    # now it should raise
    thing: Dict[str, Any] = await mongo.db.things.find_one_or_404(
        {"_id": "thing"}
        )
    assert thing["val"] == "foo"
