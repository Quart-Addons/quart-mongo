"""
quart_mongo.odmantic
"""
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from quart import Quart

from quart_mongo.config import MongoConfig, register_helpers

from .wrappers import AIOEngine


# pylint: disable=W1113


class Odmantic:
    """
    Manages MongoDB connections for your Quart app using `~odmantic`.

    Odmantic objects provide access to the MongoDB server via the :attr:`engine`
    and :attr:`cx` attributes. You must either pass the :class:`~quart.Quart`
    app to the constructor, or call :meth:`init_app`.

    Motor accepts a MongoDB URI via the ``MONGO_URI`` Quart configuration
    variable, or as an argument to the constructor or ``init_app``. See
    :meth:`init_app` for more detail.

    Arguments:
        app: An instance of :class:`~quart.Quart`.
        uri: MongoDB uri with or without the database name.
        args: Positional arguments for :class:`~AsyncIOMotorClient`.
        kwargs: Keyword arguments for :class:`~AsyncIOMotorClient`.
    """
    def __init__(
            self,
            app: Optional[Quart] = None,
            uri: Optional[str] = None,
            *args: Any,
            **kwargs: Any
    ) -> None:
        self.config: Optional[MongoConfig] = None
        self.cx: Optional[AsyncIOMotorClient] = None
        self.engine: Optional[AIOEngine] = None

        if app is not None:
            self.init_app(app, uri, *args, **kwargs)

    def init_app(
            self,
            app: Quart,
            uri: Optional[str] = None,
            *args: Any,
            **kwargs: Any
    ) -> None:
        """
        Initialize this :class:`Odmantic` for use.

        Configure a :class:`~motor_async.AsyncIOMotorClient`
        in the following scenarios:

        1. If ``uri`` is not ``None``, pass the ``uri`` and any positional
           or keyword arguments to :class:`~pymongo.mongo_client.MongoClient`
        2. If ``uri`` is ``None``, and a Flask config variable named
           ``MONGO_URI`` exists, use that as the ``uri`` as above.

        The caller is responsible for ensuring that additional positional
        and keyword arguments result in a valid call.

        If the ``uri`` does not contain the database name, then the
        :attr:`engine` will be ``None`` and will need to set it yourself.

        Arguments:
            app: An instance of :class:`~quart.Quart`.
            uri: MongoDB uri with or without the database name.
            args: Positional arguments for :class:`~AsyncIOMotorClient`.
            kwargs: Keyword arguments for :class:`~AsyncIOMotorClient`.
        """
        self.config = MongoConfig(app, uri, *args, **kwargs)
        app.before_serving(self._before_serving)
        register_helpers(app)

    def _before_serving(self) -> None:
        """
        Before Serving Function (Private)

        This function is registered with application with the
        :attr:`~Odmantic.init_app` and is called by the application before
        serving any routes.

        The purpose of the function is to setup `AsyncIOMotorClient` and also
        `AIOEngine`.
        """
        if self.config is None:
            raise ValueError("MongoDB Config for Motor is ``None``")

        self.cx = AsyncIOMotorClient(*self.config.args, **self.config.kwargs)

        if self.config.database_name:
            self.engine = AIOEngine(
                client=self.cx, database=self.config.database_name
                )
