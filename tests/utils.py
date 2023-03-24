"""
Utils for tests.
"""
import time
from quart_mongo import Mongo

class CouldNotConnect(Exception):
    """Could not connect exception."""

def wait_until_connected(mongo: Mongo, timeout=1.0):
    """
    Wait until the database connects.
    """
    start = time.time()

    while time.time() < (start + timeout):
        if mongo.cx.nodes:
            return
        time.sleep(0.05)

    raise CouldNotConnect(f"Could not provide a mongodb connected in {timeout} seconds")
