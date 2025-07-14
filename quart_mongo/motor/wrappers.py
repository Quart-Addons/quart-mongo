"""
quart_mongo.motor.wrapper
"""
from __future__ import annotations
from typing import Any, Optional

from bson.typings import _DocumentType
from motor.core import AgnosticBaseProperties
from motor import motor_asyncio
from pymongo.collection import Collection
from pymongo.database import Database
from quart import abort

from .typing import (
    CodecOptions,
    ServerMode,
    ReadConcern,
    WriteConcern
)


class AsyncIOMotorClient(motor_asyncio.AsyncIOMotorClient):
    """
    Wrapper for :class:`AsyncIOMotorClient.MongoClient`.

    Returns instances of Quart-Mongo Motor
    :class:`~quart_mongo.motor.wrappers.Database` instead of native motor
    :class:`~AsyncIOMotorDatabase` when accessed with dot notation.
    """

    def __getitem__(self, name: str) -> AsyncIOMotorDatabase:
        """__getitem__."""
        return AsyncIOMotorDatabase(self, name)


class AsyncIOMotorDatabase(motor_asyncio.AsyncIOMotorDatabase):
    """
    Wrapper for :class:`~AsyncIOMotorDatabase`.

    Returns instances of Quart-Mongo Motor
    :class:`~quart_mongo.motor.wrappers.AsyncIOMotorCollection`
    :class:`~motor.motor_asyncio.AsyncIOMotorCollection` when accessed with \
        dot notation.
    """

    def __init__(
            self, client: AsyncIOMotorClient, name: str, **kwargs: Any
    ) -> None:
        """__init__."""
        self._client = client
        delegate = kwargs.get("_delegate") or \
            Database(client.delegate, name, **kwargs)

        super(AgnosticBaseProperties, self).__init__(delegate)

    def __getitem__(self, name: str) -> AsyncIOMotorCollection:
        """__getitem__."""
        return AsyncIOMotorCollection(self, name)


class AsyncIOMotorCollection(motor_asyncio.AsyncIOMotorCollection):
    """
    Wrapper for :class:`~motor.motor_asyncio.AsyncIOMotorCollection`
    with helpers.
    """
    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        name: str,
        codec_options: Optional[CodecOptions] = None,
        read_preference: Optional[ServerMode] = None,
        write_concern: Optional[WriteConcern] = None,
        read_concern: Optional[ReadConcern] = None,
        _delegate: Optional[Any] = None,
    ) -> None:
        db_class = AsyncIOMotorDatabase

        if not isinstance(database, db_class):
            raise TypeError(
                f"First argument to MotorCollection must be \
                    MotorDatabase, not {database}"
            )

        delegate = _delegate if _delegate is not None else Collection(
            database.delegate,
            name,
            codec_options=codec_options,
            read_preference=read_preference,
            write_concern=write_concern,
            read_concern=read_concern,
        )

        super(AgnosticBaseProperties, self).__init__(delegate)
        self.database = database

    def __getitem__(self, name: str) -> AsyncIOMotorCollection:
        return AsyncIOMotorCollection(
            self.database,
            self.name + "." + name,
            _delegate=self.delegate[name]
        )

    async def find_one_or_404(
            self, *args: Any, **kwargs: Any
    ) -> _DocumentType:
        """
        Find a single document or raise a 404 with the browser.

        This function is like `AsyncIOMotorCollection.Collection.find_one`, but
        rather than returning ``None``. It will raise a 404 error (Not Found
        HTTP status) on the request.

        .. code-block:: python
            @app.route("/user/<username>")
            async def user_profile(username):
                user = await motor.cx.db.users.find_one_or_404({"_id": username})
                return await render_template("user.html",
                    user=user)

        Parameters:
            args: Arguments to be passed to
                `AsyncIOMotorCollection.Collection.find_one`.
            kwargs: Extra arguments to be passed to
                `AsyncIOMotorCollection.Collection.find_one`.
        """
        found = await self.find_one(*args, **kwargs)
        if found is None:
            abort(404)
        return found
