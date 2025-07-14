"""
tests.gridfs.test_send_file
"""
import warnings
from hashlib import md5, sha1
from io import BytesIO
from typing import Any, Dict

import pytest

from gridfs.asynchronous import AsyncGridFS
from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo import PyMongo


@pytest.mark.asyncio
async def test_404s_for_missing_file(mongo: PyMongo) -> None:
    """
    Test that `quart_mongo.Mongo.send_file` sends 404
    (not found)
    """
    with pytest.raises(NotFound):
        await mongo.send_file("no-such_file.txt")


@pytest.mark.asyncio
async def test_sets_content_type(test_app: Quart, mongo: PyMongo) -> None:
    """
    Test that the `quart_mongo.Mongo.send_file` sets
    the content type.
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", file)

    async with test_app.test_request_context("/"):
        resp = await mongo.send_file("myfile.txt")
        assert resp.content_type.startswith("text/plain")


@pytest.mark.asyncio
async def test_sends_file_to_another_db(
    test_app: Quart, mongo: PyMongo
) -> None:
    """
    Test that the `quart_mongo.Mongo.send_file` can
    send to another database.
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("my_other_file.txt", file, db="other")

    async with test_app.test_request_context("/"):
        resp = await mongo.send_file("my_other_file.txt", db="other")
        assert resp.content_type.startswith("text/plain")


@pytest.mark.asyncio
async def test_sets_content_length(test_app: Quart, mongo: PyMongo) -> None:
    """
    Test that the `quart_mongo.Mongo.send_file` sets
    the content type.
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", file)

    async with test_app.test_request_context("/"):
        resp = await mongo.send_file("myfile.txt")
        assert resp.content_length == len(file.getvalue())


@pytest.mark.asyncio
async def test_sets_supports_conditional_gets(
    test_app: Quart, mongo: PyMongo
) -> None:
    """
    Test that `quart_mongo.Mongo` supports
    conditional gets
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", file)

    environ_args: Dict[str, Any] = {
            "path": "/",
            "method": "GET",
            "headers": {
                "If-None-Match": sha1(file.getvalue()).hexdigest(),
            },
        }

    async with test_app.test_request_context(**environ_args):
        resp = await mongo.send_file("myfile.txt")
        assert resp.status_code == 304


@pytest.mark.asyncio
async def test_sets_supports_conditional_gets_md5(
    test_app: Quart, mongo: PyMongo
) -> None:
    """
    Test that `quart_mongo.Mongo` supports
    conditional gets for md5
    """
    file = BytesIO(b"a" * 500 * 1024)
    md5_hash = md5(file.getvalue()).hexdigest()

    environ_args: Dict[str, Any] = {
            "path": "/",
            "method": "GET",
            "headers": {
                "If-None-Match": md5_hash,
            },
        }

    assert mongo.db is not None
    storage = AsyncGridFS(mongo.db)

    async with storage.new_file(filename="myfile.txt") as grid_file:
        await grid_file.write(file.getvalue())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            await grid_file.set("md5", md5_hash)

    async with test_app.test_request_context(**environ_args):
        resp = await mongo.send_file("myfile.txt")
        assert resp.status_code == 304


@pytest.mark.asyncio
async def test_sets_cache_headers(
    test_app: Quart, mongo: PyMongo
) -> None:
    """
    Test that the cache headers are set
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", file)

    async with test_app.test_request_context("/"):
        resp = await mongo.send_file("myfile.txt", cache_for=60)
        assert resp.cache_control.max_age == 60
        assert resp.cache_control.public is True
