"""
tests.pymongo.gridfs.conftest
"""
from typing import AsyncGenerator

import pytest

from gridfs.asynchronous import AsyncGridFS
from quart import Quart
from quart_mongo import PyMongo


@pytest.fixture
async def mongo(test_app: Quart) -> AsyncGenerator[PyMongo, None]:
    """
    Test app for GridFS
    """
    _mongo = PyMongo(test_app)

    yield _mongo

    # teardown GridFS
    gridfs = AsyncGridFS(_mongo.db)
    files = list()

    async for gfile in gridfs.find():
        files.append(gfile)

    for gridfile in files:
        await gridfs.delete(gridfile._id)
