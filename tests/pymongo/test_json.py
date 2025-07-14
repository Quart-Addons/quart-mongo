"""
tests.pymongo.test_json
"""
import json

import pytest

from bson import ObjectId
from quart import Quart, jsonify
from quart_mongo import PyMongo


@pytest.fixture
def app(test_app: Quart) -> Quart:
    """
    App for testing json
    """
    test_app.extensions["mongo"] = PyMongo(app=test_app)
    return test_app


@pytest.mark.asyncio
async def test_encodes_json(app: Quart) -> None:
    """
    Test that json encodes
    """
    async with app.test_request_context("/"):
        resp = jsonify({"foo": "bar"})
        data = await resp.get_data()
        dumped = json.loads(data)
        assert dumped == {"foo": "bar"}


@pytest.mark.asyncio
async def test_handles_pymongo_types(app: Quart) -> None:
    """
    Test that json handles pymongo types
    """
    async with app.test_request_context("/"):
        oid = "5cf29abb5167a14c9e6e12c4"
        resp = jsonify({"id": ObjectId(oid)})
        data = await resp.get_data()
        dumped = json.loads(data)
        assert dumped == {"id": {"$oid": oid}}


@pytest.mark.asyncio
async def test_jsonifies_a_cursor(app: Quart) -> None:
    """
    Test that json handles pymongo cursor
    """
    async with app.test_request_context("/"):
        mongo: PyMongo = app.extensions["mongo"]
        assert mongo.db is not None
        await mongo.db.rows.insert_many([{"foo": "bar"}, {"foo": "baz"}])

        curs = list()
        async for data in mongo.db.rows.find(
                projection={"_id": False}).sort("foo"):
            curs.append(data)

        resp = jsonify(curs)
        data = await resp.get_data()
        dumped = json.loads(data)
        assert dumped == [{"foo": "bar"}, {"foo": "baz"}]
