"""
Tests JSON Provider for MongoDB.
"""
import json
import pytest

from bson import ObjectId
from quart import Quart, jsonify, request, Response
from six import ensure_str
from quart_mongo import Mongo
from quart_mongo.helpers import MongoJSONProvider

from tests.utils import teardown

@pytest.mark.asyncio
async def test_provider_registered_with_app(client_uri: str) -> None:
    """
    Tests that the JSON provider was registered
    with the app.
    """
    app = Quart(__name__)
    Mongo(app, client_uri)
    assert isinstance(app.json, MongoJSONProvider)

@pytest.mark.asyncio
async def test_encodes_json(client_uri: str) -> None:
    """
    Tests the encoding to JSON.
    """
    app = Quart(__name__)
    Mongo(app, client_uri)
    async with app.app_context():
        resp = jsonify({"foo": "bar"})
        dumped = json.loads(ensure_str(await resp.get_data()))
        assert dumped == {"foo": "bar"}

@pytest.mark.asyncio
async def test_handles_mongo_types(uri: str) -> None:
    """
    Tests that JSON encoding handles Mongo types.
    """
    app = Quart(__name__)
    Mongo(app, uri)
    obj_id = "5cf29abb5167a14c9e6e12c4"

    @app.route("/get", methods=["GET"])
    async def get() -> Response:
        """
        Returns a JSON response for testing.
        """
        return jsonify({"id": ObjectId(obj_id)})

    @app.route("/post", methods=["POST"])
    async def post():
        """
        Gets JSON from a request object.
        """
        data = await request.json()
        assert data == {"id": {"$oid": obj_id}}

    client = app.test_client()
    response = await client.get("/get")
    data = await response.get_json()
    await client.post("/post", json=data)

@pytest.mark.asyncio
async def test_jsonifies_cursor(uri: str) -> None:
    """
    Test JSON encoding for Mongo cursor.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)

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
    client = app.test_client()
    response = await client.get("/get")
    data = await response.get_json()
    await client.post("/post", json=data)
    await teardown(mongo)
