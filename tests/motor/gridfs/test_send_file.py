"""
tests.motor.gridfs.test_send_file
"""
from hashlib import sha1
from io import BytesIO
from typing import Any, Dict

import pytest

from quart import Quart
from werkzeug.exceptions import NotFound
from quart_mongo import Motor


@pytest.mark.asyncio
async def test_404s_for_missing_file(mongo: Motor) -> None:
    """
    Test that `quart_mongo.Mongo.send_file` sends 404
    (not found)
    """
    with pytest.raises(NotFound):
        await mongo.send_file("no-such_file.txt")


@pytest.mark.asyncio
async def test_sets_content_type(app: Quart, mongo: Motor) -> None:
    """
    Test that the `quart_mongo.Mongo.send_file` sets
    the content type.
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", file)

    async with app.test_request_context("/"):
        resp = await mongo.send_file("myfile.txt")
        assert resp.content_type.startswith("text/plain")


@pytest.mark.asyncio
async def test_sends_file_to_another_db(
    app: Quart, mongo: Motor
) -> None:
    """
    Test that the `quart_mongo.Mongo.send_file` can
    send to another database.
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("my_other_file.txt", file, db="other")

    async with app.test_request_context("/"):
        resp = await mongo.send_file("my_other_file.txt", db="other")
        assert resp.content_type.startswith("text/plain")


@pytest.mark.asyncio
async def test_sets_content_length(app: Quart, mongo: Motor) -> None:
    """
    Test that the `quart_mongo.Mongo.send_file` sets
    the content type.
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", file)

    async with app.test_request_context("/"):
        resp = await mongo.send_file("myfile.txt")
        assert resp.content_length == len(file.getvalue())


@pytest.mark.asyncio
async def test_sets_supports_conditional_gets(
    app: Quart, mongo: Motor
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

    async with app.test_request_context(**environ_args):
        resp = await mongo.send_file("myfile.txt")
        assert resp.status_code == 304


@pytest.mark.asyncio
async def test_sets_cache_headers(
    app: Quart, mongo: Motor
) -> None:
    """
    Test that the cache headers are set
    """
    file = BytesIO(b"a" * 500 * 1024)
    await mongo.save_file("myfile.txt", file)

    async with app.test_request_context("/"):
        resp = await mongo.send_file("myfile.txt", cache_for=60)
        assert resp.cache_control.max_age == 60
        assert resp.cache_control.public is True
