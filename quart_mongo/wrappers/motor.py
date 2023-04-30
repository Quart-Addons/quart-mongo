"""
quart_mongo.wrappers.motor
"""
from __future__ import annotations
from typing import Dict, Optional, TYPE_CHECKING

from motor import motor_asyncio
from motor.core import AgnosticBaseProperties
from pymongo.collection import Collection
from pymongo.database import Database
from quart import abort

from quart_mongo.typing import (
    CodecOptions,
    ServerMode,
    ReadConcern,
    WriteConcern
)

if TYPE_CHECKING:
    from .client import AIOMotorClient

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
        read_preference: Optional[ServerMode]=None,
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
