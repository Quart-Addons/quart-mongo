"""
quart_mongo.pymongo.wrappers
"""
from __future__ import annotations
from typing import Any

from bson.typings import _DocumentType
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from quart import abort


# pylint: disable=W0223

class MongoClient(AsyncMongoClient[_DocumentType]):
    """
    Wrapper for :class:`~pymongo.asynchronous.mongo_client.AsyncMongoClient`.

    Returns instances of Quart-Mongo
    :class:`~quart_mongo.wrappers.Database` instead of native PyMongo
    :class:`~pymongo.asynchronous.database.Database` when accessed with
        dot notation.
    """
    def __getattr__(self, name: str) -> Database[_DocumentType]:
        attr = super().__getattr__(name)
        if isinstance(attr, AsyncDatabase):
            return Database(self, name)
        return attr

    def __getitem__(self, name: str) -> Database[_DocumentType]:
        item_ = super().__getitem__(name)
        if isinstance(item_, AsyncDatabase):
            return Database(self, name)
        return item_


class Database(AsyncDatabase[_DocumentType]):
    """
    Wrapper for :class:`~pymongo.asynchronous.database.Database`.

    Returns instances of Quart_Mongo
    :class:`~quart_mongo.wrappers.Collection` instead of native PyMongo
    :class:~pymongo.asynchronous.collection.AsyncCollection when accessed
        with dot notation.
    """
    def __getattr__(self, name: str) -> Collection[_DocumentType]:
        attr = super().__getattr__(name)
        if isinstance(attr, AsyncCollection):
            return Collection(self, name)
        return attr

    def __getitem__(self, name: str) -> Collection[_DocumentType]:
        item_ = super().__getitem__(name)
        if isinstance(item_, AsyncCollection):
            return Collection(self, name)
        return item_


class Collection(AsyncCollection[_DocumentType]):
    """
    Subclass of Pymongo \
        :class:`~pymongo.asynchronous.collection.AsyncCollection`
    with helpers.
    """
    def __getattr__(self, name: str) -> Collection[_DocumentType]:
        attr = super().__getattr__(name)
        if isinstance(attr, AsyncCollection):
            db = self._database
            return Collection(db, attr.name)
        return attr

    def __getitem__(self, name: str) -> Collection[_DocumentType]:
        item = super().__getitem__(name)
        if isinstance(item, AsyncCollection):
            db = self._database
            return Collection(db, name)
        return item

    async def find_one_or_404(
            self, *args: Any, **kwargs: Any
    ) -> _DocumentType:
        """
        Find a single document or raise a 404.

        This is like \
            :meth:`~pymongo.asynchronous.collection.AsyncCollection.find_one`,
        but rather than returning ``None``, cause a 404 Not Found HTTP status
        on the request.

        .. code-block:: python

            @app.route("/user/<username>")
            async def user_profile(username):
                user = await mongo.db.users.find_one_or_404({"_id": username})
                return render_template("user.html", user=user)
        """
        found = await self.find_one(*args, **kwargs)
        if found is None:
            abort(404)
        return found


__all__ = (
    "MongoClient",
    "Database",
    "Collection"
)
