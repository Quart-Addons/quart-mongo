"""
quart_mongo.extension

The main quart_mongo extension.
"""
from typing import Any, Optional

from bson.json_util import JSONOptions
from pymongo import uri_parser
from quart import Quart, abort, current_app, request, Response

from .bson import BSONObjectIdConverter
from .json import MongoJSONProvider
from .utils import get_uri, MongoConfig
from .wrappers import AIOMotorClient, AIOMotorDatabase, AIOEngine

class Mongo(object):
    """
    This class is for integrating MongoDB into your `Quart` application. It
    intergrates with MongoDB by using `Motor` and `Odmantic`. It also provides
    a few helper functions for working with MongoDB.
    """
    def __init__(
        self,
        app: Optional[Quart] = None,
        uri: Optional[str] = None,
        json_options: Optional[JSONOptions] = None,
        *args,
        **kwargs
        ) -> None:
        """
        The constructor of the `Mongo` class. 

        Arguments:
        ----------
        app: The `quart.Quart` application. Defaults to ``None``.
        uri: The MongoDB URI to use. Defaults to ``None``.
        json_options: ``JSONOptions`` for the JSON Provider.
        args: Arguments to pass to ``AIOMotorClient``.
        kwargs: Extra arguments to pass to ``AIOMotorClient``.
        """
        self.config: MongoConfig = None
        self.cx: AIOMotorClient = None
        self.db: AIOMotorDatabase = None
        self.odm: AIOEngine = None
        self.json_options: Optional[JSONOptions] = json_options

        if app is not None:
            self.init_app(app, uri, *args, **kwargs)

    def init_app(
        self,
        app: Quart,
        uri: Optional[str] = None,
        *args,
        **kwargs
        ) -> None:
        """
        This function configures `Mongo` and applies the extension instance
        with the given application.

        Arguments:
        ----------
        app: The `quart.Quart` application. Defaults to ``None``.
        uri: The MongoDB URI to use. Defaults to ``None``.
        args: Arguments to pass to ``AIOMotorClient``.
        kwargs: Extra arguments to pass to ``AIOMotorClient``.
        """
        uri = get_uri(app, uri)
        args = tuple([uri] + list(args))
        parsed_uri = uri_parser.parse_uri(uri)
        database_name = parsed_uri["database"] or None

        # Try to delay connecting, in case the app is loaded before forking, per
        # https://pymongo.readthedocs.io/en/stable/faq.html#is-pymongo-fork-safe
        kwargs.setdefault("connect", False)

        self.config = MongoConfig(
            uri=uri,
            database=database_name,
            args=args,
            kwargs=kwargs
        )

        app.before_serving(self._before_serving)

        # Setup BSON Converter
        if app.config.setdefault("MONGO_BSON_CONVERTER", True) and \
            "ObjectId" not in app.url_map.converters:
            app.url_map.converters["ObjectId"] = BSONObjectIdConverter

        # Setup JSON Provider
        if app.config.setdefault("MONGO_JSON_PROVIDER", True) and \
            not isinstance(app.json, MongoJSONProvider):
            app.json = MongoJSONProvider(app, self.json_options)

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

    async def send_file(self):
        pass

    async def save_file(self):
        pass
