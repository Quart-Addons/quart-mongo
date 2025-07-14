"""
tests.pymongo.gridfs.test_save_file
"""
from io import BytesIO

import pytest

from bson import ObjectId
from gridfs.asynchronous import AsyncGridFS
from quart_mongo import PyMongo


@pytest.mark.asyncio
async def test_saves_file(mongo: PyMongo) -> None:
    """
    Test save file function from `quart_mongo.Mongo.saves_file`
    """
    fileobj = BytesIO(b"these are the bytes")

    await mongo.save_file("my-file", fileobj)
    assert mongo.db is not None
    gridfs = AsyncGridFS(mongo.db)
    assert await gridfs.exists({"filename": "my-file"})


@pytest.mark.asyncio
async def test_saves_file_to_another_db(mongo: PyMongo) -> None:
    """
    Test save file function from `quart_mongo.Mongo.saves_file`
    using db other than 'fs'
    """
    fileobj = BytesIO(b"these are the bytes")

    await mongo.save_file("my-file", fileobj, db="other")
    assert mongo.cx is not None
    gridfs = AsyncGridFS(mongo.cx["other"])
    assert await gridfs.exists({"filename": "my-file"})


@pytest.mark.asyncio
async def test_saves_files_with_props(mongo: PyMongo) -> None:
    """
    Test that the file is saved with properties.
    """
    fileobj = BytesIO(b"these are the bytes")

    await mongo.save_file("my-file", fileobj, foo="bar")
    assert mongo.db is not None
    gridfs = AsyncGridFS(mongo.db)
    gridfile = await gridfs.find_one({"filename": "my-file"})
    assert gridfile is not None
    assert gridfile.foo == "bar"


@pytest.mark.asyncio
async def test_returns_oid(mongo: PyMongo) -> None:
    """
    Test save file function from `quart_mongo.Mongo.saves_file`
    returns a `bson.ObjectId`.
    """
    fileobj = BytesIO(b"these are the bytes")

    oid = await mongo.save_file("my-file", fileobj)

    assert isinstance(oid, ObjectId)
