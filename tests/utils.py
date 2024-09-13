"""
tests.utils
"""
import time
from quart_mongo import Mongo


async def teardown(mongo: Mongo, database: str | None = None) -> None:
    """
    Tears down the MongoDB once the test is completed.
    """
    if database is None:
        if mongo.database is not None:
            database = mongo.database
        else:
            database = "test"
    await mongo.cx.drop_database(database)


class CouldNotConnect(Exception):
    """
    Could not connect exception.
    """


def wait_until_connected(mongo: Mongo, timeout: float = 1.0) -> None:
    """
    Wait until the database connects.
    """
    start = time.time()

    while time.time() < (start + timeout):
        if mongo.cx.nodes:
            return
        time.sleep(0.5)

    raise CouldNotConnect(
        f"Could not provide a mongodb connected in {timeout} seconds"
        )
