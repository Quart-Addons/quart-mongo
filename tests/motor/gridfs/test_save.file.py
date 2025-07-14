"""
tests.motor.gridfs.test_save_file
"""
from io import BytesIO

import pytest

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from quart_mongo import Motor


@pytest.mark.asyncio
async def test_saves_file(mongo: Motor) -> None:
    """
    Test save file function from `quart_mongo.Mongo.saves_file`
    """
    fileobj = BytesIO(b"these are the bytes")

    oid = await mongo.save_file("my-file", fileobj)
    assert mongo.db is not None
    storage = AsyncIOMotorGridFSBucket(mongo.db)
    gridfile = await storage.open_download_stream(oid)
    assert gridfile.filename == "my-file"


@pytest.mark.asyncio
async def test_saves_file_to_another_db(mongo: Motor) -> None:
    """
    Test save file function from `quart_mongo.Mongo.saves_file`
    using db other than 'fs'
    """
    fileobj = BytesIO(b"these are the bytes")

    oid = await mongo.save_file("my-file", fileobj, db="other")
    assert mongo.cx is not None
    storage = AsyncIOMotorGridFSBucket(mongo.cx["other"])
    gridfile = await storage.open_download_stream(oid)
    assert gridfile.filename == "my-file"


@pytest.mark.asyncio
async def test_saves_files_with_props(mongo: Motor) -> None:
    """
    Test that the file is saved with properties.
    """
    fileobj = BytesIO(b"these are the bytes")

    oid = await mongo.save_file("my-file", fileobj, foo="bar")
    assert mongo.db is not None
    storage = AsyncIOMotorGridFSBucket(mongo.db)
    gridfile = await storage.open_download_stream(oid)
    assert gridfile.metadata is not None
    assert gridfile.metadata["foo"] == "bar"


@pytest.mark.asyncio
async def test_returns_oid(mongo: Motor) -> None:
    """
    Test save file function from `quart_mongo.Mongo.saves_file`
    returns a `bson.ObjectId`.
    """
    fileobj = BytesIO(b"these are the bytes")

    oid = await mongo.save_file("my-file", fileobj)

    assert isinstance(oid, ObjectId)
