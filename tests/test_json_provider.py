"""
Tests JSON provider for MongoDB.
"""
import json
import pytest

from bson import ObjectId
from quart import Quart, jsonify, request, Response
from quart.typing import TestClientProtocol
from six import ensure_str
from quart_mongo import Mongo, MongoJSONProvider

from .utils import teardown

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
async def test_handles_mongo_types(
    app: Quart, uri: str, client: TestClientProtocol
    ) -> None:
    """
    Tests that JSON encoding handles Mongo types.
    """
    Mongo(app, uri)
    id = "5cf29abb5167a14c9e6e12c4"

    @app.route("/get", methods=["GET"])
    async def get() -> Response:
        """
        Returns a JSON response for testing.
        """
        return jsonify({"id": ObjectId(id)})

    @app.route("/post", methods=["POST"])
    async def post():
        """
        Gets JSON from a request object.
        """
        data = await request.json()
        assert data == {"id": {"$oid": id}}

    response = await client.get("/get")
    data = await response.get_json()
    await client.post("/post", json=data)

@pytest.mark.asyncio
async def test_jsonifies_cursor(
    app: Quart, mongo_uri: Mongo, client: TestClientProtocol
    ) -> None:
    """
    Test JSON encoding for Mongo cursor.
    """
    mongo = mongo_uri

    @app.route("/get", methods=["GET"])
    async def get() -> Response:
        """
        Returns a JSON response for testing.
        """
        await mongo.db.rows.insert_many([{"foo": "bar"}, {"foo": "baz"}])
        curs = await mongo.db.row.find(projection={"_id": False})
        curs = curs.sort("foo")
        return jsonify(curs)

    @app.route("/post", methods=["POST"])
    async def post():
        """
        Gets JSON from a request object.
        """
        data = await request.json()
        assert data == [{"foo": "bar"}, {"foo": "baz"}]

    await app.startup()
    response = await client.get("/get")
    data = await response.get_json()
    await client.post("/post", json=data)
    await teardown(mongo)
