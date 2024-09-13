"""
quart_mongo.wrappers
"""
from __future__ import annotations
from typing import Any, Dict, Optional, Type, Union

from motor.core import AgnosticBaseProperties
from motor import motor_asyncio
from odmantic import AIOEngine as _AIOEngine, Model
from odmantic.engine import ModelType
from odmantic.query import QueryExpression
from pymongo.collection import Collection
from pymongo.database import Database
from quart import abort

from quart_mongo.typing import (
    CodecOptions,
    ServerMode,
    ReadConcern,
    WriteConcern
)


class AIOMotorDatabase(motor_asyncio.AsyncIOMotorDatabase):
    """
    Subclass of :class:`~motor.motor_asyncio.AsyncIOMotorDatabase`.

    Returns instances :class:`~quart_mongo.wrappers.AsyncMotorCollection`
    instead of native :class:`~motor.motor_asyncio.AsyncIOMotorCollection` when
    accessed with dot notation.

    Arguments:
        client: An instance of the Motor client to use to connect to the
            database.
        name: The name of the database.
        kwargs: Extra arguments to be passed to the database.
    """

    def __init__(
            self,
            client: AIOMotorClient,
            name: str,
            **kwargs: Any
    ) -> None:
        self._client = client
        delegate = kwargs.get("_delegate") or \
            Database(client.delegate, name, **kwargs)

        super(AgnosticBaseProperties, self).__init__(delegate)

    def __getitem__(self, name: str) -> AIOMotorCollection:
        return AIOMotorCollection(self, name)


class AIOMotorCollection(motor_asyncio.AsyncIOMotorCollection):
    """
    Subclass of the :class:`~motor.motor_asyncio.AsyncIOMotorCollection`
    with helpers.
    """
    def __init__(
        self,
        database: AIOMotorDatabase,
        name: str,
        codec_options: Optional[CodecOptions] = None,
        read_preference: Optional[ServerMode] = None,
        write_concern: Optional[WriteConcern] = None,
        read_concern: Optional[ReadConcern] = None,
        _delegate: Optional[Any] = None,
    ) -> None:
        db_class = AIOMotorDatabase

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

    def __getitem__(self, name: str) -> AIOMotorCollection:
        return AIOMotorCollection(
            self.database,
            self.name + "." + name,
            _delegate=self.delegate[name]
        )

    async def find_one_or_404(self, *args: Any, **kwargs: Any) -> Dict:
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
            args: Arguments to be passed to
                `AsyncIOMotorCollection.Collection.find_one`.
            kwargs: Extra arguments to be passed to
                `AsyncIOMotorCollection.Collection.find_one`.
        """
        found = await self.find_one(*args, **kwargs)
        if found is None:
            abort(404)
        return found


class AIOEngine(_AIOEngine):
    """
    Subclass of the :class`~Odmantic.AIOEngine` object, which is responsible
    for handling database operations with MongoDB in an asynchronous way using
    `Motor`.

    The purpose of this subclass is to add the function
    :func::`AIOEngine.find_one_or_404`.
    """
    async def find_one_or_404(
            self,
            model: Type[ModelType],
            *queries: Union[
                QueryExpression, Dict, bool
            ],
            sort: Optional[Any],
            session: Optional[Any] = None
    ) -> Model:
        """
        Find a single document or raise a 404 with the browser.

        This function is like :meth:`~odmantic.AIOEngine.find_one`, but rather
        than returning ``None``. It will raise a 404 error (Not Found HTTP
        status) on the request.

        .. code-block:: python
            @app.route("/user/<username>")
            async def user_profile(username):
                user = await odmantic.db..find_one_or_404(model, {"_id": username})
                return await render_template("user.html",
                    user=user)

        Parameters:
            model: The :class:`~Odmantic.Model` to use to find the model.
            args: Arguments to pass to :class:`~odmantic.AIOEngine.find_one`.
            kwargs: Extra arguments to pass to
            :class:`~odmantic.AIOEngine.find_one`.

        Raises:
            ``HTTPException``: Uses `quart.abort` to raises this exception if
            there is not entry found in the database. This will raise a 404
            error code with the browser.
        """
        found = await self.find_one(
            model,
            *queries,
            sort,
            session
            )

        if found is None:
            abort(404)

        return found


class AIOMotorClient(motor_asyncio.AsyncIOMotorClient):
    """
    Subclass of :class:`~motor.motor_asyncio.AsyncIOMotorClient`.

    Returns instances of Quart-Mongo
    :class:`~quart_mongo.wrappers.AIOMotorDatabase` instead of native
    :class:`~motor.motor_asyncio.AIOMotorDatabase`.
    :class:`~quart_mongo.wrappers.AIOEngine` instead of native
    :class:`~odmantinc.AIOEngine`.
    """

    def __getitem__(self, name: str) -> AIOMotorDatabase:
        """
        Returns an instance of :class:`~quart_mongo.wrappers.AIOMotorDatabase`.
        """
        return AIOMotorDatabase(self, name)

    def motor(self, name: str) -> AIOMotorDatabase:
        """
        Returns an instance of :class:`~quart_mongo.wrappers.AIOMotorDatabase`.
        """
        return AIOMotorDatabase(self, name)

    def odm(self, name: str) -> AIOEngine:
        """
        Returns an instance of :class:`~quart_mongo.wrappers.AIOEngine`.
        """
        return AIOEngine(self, name)
