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

from tests.utils import teardown

@pytest.mark.asyncio
async def test_saves_file(uri: str) -> None:
    """
    Tests if saves file.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    fileobj = BytesIO(b"these are the bytes")
    await mongo.save_file("my-file", fileobj)
    gridfs = AsyncIOMotorGridFSBucket(mongo.db)
    assert gridfs.find({"filename": "my-file"})
    await teardown(mongo)

@pytest.mark.asyncio
async def test_guess_type_from_filename(uri: str) -> None:
    """
    Test guess type for mimetype.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    fileobj = BytesIO(b"these are the bytes")
    id = await mongo.save_file("my-file.txt", fileobj)
    storage = AsyncIOMotorGridFSBucket(mongo.db)
    gridfile = await storage.open_download_stream(id)
    assert gridfile.content_type == "text/plain"
    await teardown(mongo)

@pytest.mark.asyncio
async def test_saves_files_with_props(uri: str) -> None:
    """
    Tests save files with properties.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    fileobj = BytesIO(b"these are the bytes")
    await mongo.save_file("my-file", fileobj, foo = "bar")
    storage = AsyncIOMotorGridFSBucket(mongo.db)
    gridfile = await storage.open_download_stream_by_name("my-file")
    assert gridfile.metadata["foo"] == "bar"
    await teardown(mongo)

@pytest.mark.asyncio
async def test_returns_id(uri: str) -> None:
    """
    Tests the return id from `Mongo.save_file` is
    an instance of `bson.ObjectId`.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    fileobj = BytesIO(b"these are the bytes")
    _id = await mongo.save_file("my-file", fileobj, foo = "bar")
    assert isinstance(_id, ObjectId)
    await teardown(mongo)

@pytest.mark.asyncio
async def test_404s_for_missing_files(uri: str) -> None:
    """
    Tests that the extension will raise a 404 (Not Found)
    if the file does not exists.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    with pytest.raises(NotFound):
        await mongo.send_file("no-such-file.txt")
    await teardown(mongo)

@pytest.mark.asyncio
async def test_sets_content_types(uri: str) -> None:
    """
    Tests content type for the response.
    """
    app = Quart(__name__)
    mongo = Mongo(app, uri)
    await app.startup()
    fileobj = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", fileobj)

    async with app.test_request_context("/"):
        resp = await mongo.send_file("myfile.txt")
        assert resp.content_type.startswith("text/plain")
    await teardown(mongo)
