"""
Tests GridFS with MongoDB.
"""
from hashlib import md5
from io import BytesIO

import pytest
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo import Mongo

from .utils import teardown

@pytest.mark.asyncio
async def test_saves_file(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Tests if saves file.
    """
    mongo = mongo_uri
    await app.startup()
    fileobj = BytesIO(b"these are the bytes")
    await mongo.save_file("my-file", fileobj)
    gridfs = AsyncIOMotorGridFSBucket(mongo.db)
    assert gridfs.find({"filename": "my-file"})
    await teardown(mongo)

@pytest.mark.asyncio
async def test_guess_type_from_filename(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Test guess type for mimetype.
    """
    mongo = mongo_uri
    await app.startup()
    fileobj = BytesIO(b"these are the bytes")
    id = await mongo.save_file("my-file.txt", fileobj)
    storage = AsyncIOMotorGridFSBucket(mongo.db)
    gridfile = await storage.open_download_stream(id)
    assert gridfile.content_type == "text/plain"
    await teardown(mongo)

@pytest.mark.asyncio
async def test_saves_files_with_props(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Tests save files with properties.
    """
    mongo = mongo_uri
    await app.startup()
    fileobj = BytesIO(b"these are the bytes")
    await mongo.save_file("my-file", fileobj, foo = "bar")
    storage = AsyncIOMotorGridFSBucket(mongo.db)
    gridfile = await storage.open_download_stream_by_name("my-file")
    assert gridfile.metadata["foo"] == "bar"
    await teardown(mongo)

@pytest.mark.asyncio
async def test_returns_id(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Tests the return id from `Mongo.save_file` is
    an instance of `bson.ObjectId`.
    """
    mongo = mongo_uri
    await app.startup()
    fileobj = BytesIO(b"these are the bytes")
    _id = await mongo.save_file("my-file", fileobj, foo = "bar")
    assert isinstance(_id, ObjectId)
    await teardown(mongo)

@pytest.mark.asyncio
async def test_404s_for_missing_files(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Tests that the extension will raise a 404 (Not Found)
    if the file does not exists.
    """
    mongo = mongo_uri
    await app.startup()
    with pytest.raises(NotFound):
        await mongo.send_file("no-such-file.txt")
    await teardown(mongo)

@pytest.mark.asyncio
async def test_sets_content_types(
    app: Quart, mongo_uri: Mongo
    ) -> None:
    """
    Tests content type for the response.
    """
    mongo = mongo_uri
    await app.startup()
    fileobj = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", fileobj)

    async with app.test_request_context("/"):
        resp = await mongo.send_file("myfile.txt")
        assert resp.content_type.startswith("text/plain")
    await teardown(mongo)
