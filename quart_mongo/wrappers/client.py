"""
quart_mongo.wrappers.client
"""
from motor import motor_asyncio

from .engine import AIOEngine
from .motor import AIOMotorDatabase

class AIOMotorClient(motor_asyncio.AsyncIOMotorClient):
    """
    Subclass of `motor_asyncio.AsyncIOMotorDatabase`.

    Returns instances of Quart-Mongo `quart_mongo.wrappers.AsyncMotorClient`
    instead of native Pymongo `motor.motor_asyncio.AsyncIOMotorClient` when
    accessed with dot notation.
    """

    def __getitem__(self, name: str) -> AIOMotorDatabase:
        """__getitem__."""
        return AIOMotorDatabase(self, name)

    def motor(self, name: str) -> AIOMotorDatabase:
        """
        Returns an instnace of `AIOMotorDatabase`.
        """
        return AIOMotorDatabase(self, name)

    def odm(self, name: str) -> AIOEngine:
        """
        Returns an instance of `AIOEngine`.
        """
        return AIOEngine(self, name)
