"""
quart_mongo.wrappers

Wrappers for Motor and Odmantic.
"""
from __future__ import annotations
from typing import Dict, Optional

from bson.codec_options import CodecOptions
from motor import motor_asyncio
from motor.core import AgnosticBaseProperties
from odmantic import AIOEngine as _AIOEngine, Model
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.read_preferences import _ServerMode
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from quart import abort

class AIOMotorCollection(motor_asyncio.AsyncIOMotorCollection):
    """
    Subclass of the `AsyncIOMotorCollection` from Motor with helpers.
    Sub-class of Motor :class:`~AsyncIOMotorCollection` with helpers.
    """
    def __init__(
        self,
        database: AIOMotorDatabase,
        name: str,
        codec_options: Optional[CodecOptions]=None,
        read_preference: Optional[_ServerMode]=None,
        write_concern: Optional[WriteConcern]=None,
        read_concern: Optional[ReadConcern]=None,
        _delegate=None,
    ) -> None:
        """
        The constructor of `AIOMotorCollection`.
        """
        db_class = AIOMotorDatabase

        if not isinstance(database, db_class):
            raise TypeError(
                f"First argument to MotorCollection must be \
                    MotorDatabase, not {database}"
            )

        delegate = _delegate or Collection(
            database.delegate,
            name,
            codec_options=codec_options,
            read_preference=read_preference,
            write_concern=write_concern,
            read_concern=read_concern,
        )

        super(AgnosticBaseProperties, self).__init__(delegate)
        self.database = database

    def __getitem__(self, name: str) -> AIOMotorCollection:
        """__getitem__."""
        return AIOMotorCollection(
            self.database, self.name + "." + name, _delegate=self.delegate[name]
        )

    async def find_one_or_404(self, *args, **kwargs) -> Dict:
        """
        Find a single document or raise a 404 with the browser.

        This function is like `AsyncIOMotorCollection.Collection.find_one`, but
        rather than returning ``None``. It will raise a 404 error (Not Found
        HTTP status) on the request.

        .. code-block:: python
            @app.route("/user/<username>")
            async def user_profile(username):
                user = await mongo.motor.database.users.find_one_or_404({"_id": username})
                return await render_template("user.html",
                    user=user)

        Parameters:
            args: Arguments to be passed to `AsyncIOMotorCollection.Collection.find_one`.
            kwargs: Extra arguments to be passed to `AsyncIOMotorCollection.Collection.find_one`.
        """
        found = await self.find_one(*args, **kwargs)
        if found is None:
            abort(404)
        return found


class AIOMotorDatabase(motor_asyncio.AsyncIOMotorDatabase):
    """
    Subclass of `AsyncIOMotorDatabase`.

    Returns instances of Quart-Mongo `quart_mongo.wrappers.AsyncMotorCollection`
    instead of native Pymongo `motor.motor_asyncio.AsyncIOMotorCollection` when
    accessed with dot notation.
    """

    def __init__(self, client: AIOMotorClient, name: str, **kwargs) -> None:
        """
        The constructor of `AIOMotorDatabase`.

        Parameters:
            client (`AIOMotorClient`): An instance of the Motor client to use to
            connect to the database.
            name (``str``): The name of the database.
            kwargs: Extra arguments to be passed to the database.
        """
        self._client = client
        delegate = kwargs.get("_delegate") or Database(client.delegate, name, **kwargs)

        super(AgnosticBaseProperties, self).__init__(delegate)

    def __getitem__(self, name: str) -> AIOMotorCollection:
        """__getitem__."""
        return AIOMotorCollection(self, name)

class AIOEngine(_AIOEngine):
    """
    Subclass of the `Odmantic.AIOEngine` object, which is responsible for handling database
    operations with MongoDB in an asynchronous way using `Motor`.

    The purpose of this subclass is to add the function :func::`AIOEngine.find_one_or_404`.
    """
    async def find_one_or_404(self, model: Model, *args, **kwargs) -> Model:
        """
        Find a single document or raise a 404 with the browser.

        This function is like :meth:`AIOEngine.find_one`, but rather than returning
        ``None``. It will raise a 404 error (Not Found HTTP status) on the request.

        .. code-block:: python
            @app.route("/user/<username>")
            async def user_profile(username):
                user = await odmantic.db..find_one_or_404(model, {"_id": username})
                return await render_template("user.html",
                    user=user)

        Parameters:
            model (``Model``): The `Odmantic.Model` to use to find the model.
            args: Arguments to pass to `AIOEngine.find_one`.
            kwargs: Extra arguments to pass to `AIOEngine.find_one`.

        Returns:
            ``Model``

        Raises:
            ``HTTPException``: Uses `quart.abort` to raises this exception if
            there is not entry found in the database. This will raise a 404
            error code with the browser.
        """
        found = await self.find_one(model, *args, **kwargs)

        if found is None:
            abort(404)

        return found

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
