"""
tests.motor.gridfs.conftest
"""
from typing import AsyncGenerator

import pytest

from gridfs.asynchronous import AsyncGridFS
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from quart import Quart
from quart_mongo import Motor


@pytest.fixture
async def mongo(app: Quart) -> AsyncGenerator[Motor, None]:
    """
    Test app for GridFS
    """
    _mongo = Motor(app)

    await app.startup()

    yield _mongo

    # teardown GridFS
    gridfs = AsyncIOMotorGridFSBucket(_mongo.db)
    files = list()

    async for gfile in gridfs.find():
        files.append(gfile)

    for gridfile in files:
        await gridfs.delete(gridfile._id)
