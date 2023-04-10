"""
Tests JSON provider for MongoDB.
"""
import json
import pytest

from bson import ObjectId
from quart import Quart, jsonify
from quart_mongo import Mongo, MongoJSONProvider
from six import ensure_str

@pytest.mark.asyncio
async def test_provider_registered_with_app(
    app: Quart, client_uri: Mongo
    ) -> None:
    """
    Tests that the JSON provider was registered
    with the app.
    """
    Mongo(app, client_uri)
    assert isinstance(app.json, MongoJSONProvider)

@pytest.mark.asyncio
async def test_encodes_json(app: Quart) -> None:
    """
    Tests the encoding to JSON.
    """
    async with app.app_context():
        resp = jsonify({"foo": "bar"})
        dumped = json.loads(ensure_str(await resp.get_data()))
        assert dumped == {"foo": "bar"}

@pytest.mark.asyncio
async def test_handles_mongo_types(app: Quart, client_uri: str) -> None:
    """
    Tests that JSON encoding handles Mongo types.
    """
    Mongo(app, client_uri)
    async with app.app_context():
        resp = jsonify({"id": ObjectId("5cf29abb5167a14c9e6e12c4")})
        dumped = app.json.loads(ensure_str(await resp.get_data()))
        assert dumped == {"id": {"$oid": "5cf29abb5167a14c9e6e12c4"}}

