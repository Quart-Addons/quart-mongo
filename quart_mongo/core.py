"""
quart_mongo.core

The extension for Quart Mongo.
"""
from __future__ import annotations
import typing as t

from bson.json_util import JSONOptions
from pymongo import uri_parser
from quart import Quart, abort, current_app, request

from .bson import BSONObjectIdConverter
from .config import MongoConfig, _get_uri
from .json import MongoJSONProvider
from .wrappers import AIOMotorClient, AIOMotorDatabase, AIOEngine

class Mongo(object):
    """
    This class is for integrating MongoDB into your `Quart` application. It
    intergrates with MongoDB by using `Motor` and `Odmantic`. It also provides
    a few helper functions for working with MongoDB.
    """
    def __init__(
            self,
            app: Quart | None = None,
            uri: str | None = None,
            json_options: JSONOptions | None = None,
            *args,
            **kwargs
            ) -> None:
        """
        The constructor of the Mongo class.

        Arguments:
            app: The `Quart` application to use. Defaults to ``None``.
            uri: The MongoDB URI to use. This parameter defaults to ``None``
            and will then use the app config.
            json_options: Options for JSON encoding.
            args: Arguments to pass to `AIOMotorClient` on intialization.
            kwargs: Extra agrugments to pass to `AIOMotorClient` on intialization.
        """
        self.config: MongoConfig = None
        self.json_options: JSONOptions | None = json_options
        self.cx: AIOMotorClient = None
        self.db: AIOMotorDatabase = None
        self.odm: AIOEngine = None
        if app is not None:
            self.init_app(app, uri, *args, **kwargs)

    def init_app(
            self,
            app: Quart,
            uri: str | None = None,
            *args,
            **kwargs
            ) -> None:
        """
        This function configures `Mongo` and applies the extension instance
        with the given application.

        Parameters:
            app: The application to use.
            uri: The MongoDB URI to use. This parameter defaults to `None`
            and will then use the app config.
            args: Arguments to pass to `AIOMotorClient` on intialization.
            kwargs: Extra arguments to pass to `AIOMotorClient` on initialization.
        """
        uri = _get_uri(app, uri)
        args = tuple([uri] + list(args))
        parsed_uri = uri_parser.parse_uri(uri)
        database_name = parsed_uri["database"] or None

        # Try to delay connecting, in case the app is loaded before forking, per
        # https://pymongo.readthedocs.io/en/stable/faq.html#is-pymongo-fork-safe
        kwargs.setdefault("connect", False)

        # Set the configuration for this instance.
        self.config = MongoConfig(
            uri=uri,
            database=database_name,
            args=args,
            kwargs=kwargs
        )

        # Register before serving function with the app
        app.before_serving(self._before_serving)

        # Register BSON converter
        if app.config.setdefault("MONGO_BSON_CONVERTER", True) and \
            "ObjectId" not in app.url_map.converters:
            app.url_map.converters["ObjectId"] = BSONObjectIdConverter

        # Register JSON Provider
        if app.config.setdefault("MONGO_JSON_PROVIDER", True) and \
            not isinstance(app.json, MongoJSONProvider):
            app.json_provider_class = MongoJSONProvider
            app.json = app.json_provider_class(app)

    async def _before_serving(self) -> None:
        """
        Before Serving Function (Private)

        This private function is registered with application with the
        `Mongo.init_app` function and is called by the application before
        serving any routes.

        The purpose of the function is to setup `AIOMotorClient` and also
        `AIOMotorDatabase` and `AIOEngine` if the MongoDB URI provides the
        database name.
        """
        self.cx = AIOMotorClient(*self.config.args, **self.config.kwargs)

        if self.config.database:
            self.db = self.cx.motor(self.config.database)
            self.odm = self.cx.odm(self.config.database)
