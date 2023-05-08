"""
quart_mongo.core

The extension for Quart Mongo.
"""
from __future__ import annotations
from inspect import isawaitable
import mimetypes
from typing import AnyStr, Optional, TYPE_CHECKING

from bson import ObjectId
from gridfs import NoFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo import uri_parser
from quart import Quart, abort, request, Response, send_file

from .const import (
    GRIDFS_CACHE,
    GRIDFS_FILEOBJ,
    GRIDFS_STRING,
    GRIDFS_VERSION
)

from .config import MongoConfig, _get_uri
from .helpers import register_mongo_helpers
from .wrappers import AIOMotorClient, AIOMotorDatabase, AIOEngine
from .typing import JSONOptions

if TYPE_CHECKING:
    from _typeshed import SupportsRead
    from motor.motor_asyncio import AsyncIOMotorGridIn

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
        app.config.setdefault("QUART_MONGO_URI", None)

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

    @staticmethod
    def register_helpers(
        app: Quart,
        bson: bool = True,
        json: bool = True,
        json_options: Optional[JSONOptions] = None,
        schema: bool = True,
        convert_casing: bool = False
    ) -> None:
        """
        This is a shortcut to `quart_mongo.helpers.register_mongo_helers` function.

        If using multiple instance of Mongo, only call this function onces to setup
        the helpers with the `Quart` app.

        Arguments:
            app: The `Quart` application.
            args: Arguments to be passed to the `register_mongo_helpers` function.
                Refer to `register_mongo_helpers` function for arguments.
        """
        register_mongo_helpers(
            app,
            bson,
            json,
            json_options,
            schema,
            convert_casing
        )

    async def send_file_by_name(
        self,
        filename: str,
        base: str = "fs",
        version: int = -1,
        cache_for: int = 31536000
        ) -> Response:
        """
        Respond with a file from GridFS.
        """
        if not isinstance(base, str):
            raise TypeError(GRIDFS_STRING)
        if not isinstance(version, int):
            raise TypeError(GRIDFS_VERSION)
        if not isinstance(cache_for, int):
            raise TypeError(GRIDFS_CACHE)

        storage = AsyncIOMotorGridFSBucket(self.db, bucket_name = base)

        try:
            grid_out = await storage.open_download_stream_by_name(filename, version)
        except NoFile:
            abort(404)

        file_obj = await grid_out.read()
        mimetype = grid_out.metadata["contentType"]

        response= await send_file(
            file_obj,
            mimetype=mimetype,
            attachment_filename=filename,
            cache_timeout=cache_for)
        response = await response.make_conditional(request)
        return response

    async def send_file_by_id(
            self,
            id: ObjectId,
            base: str = "fs",
            cache_for: int = 31536000
            ) -> Response:
        """
        Send a file by id.
        """
        storage = AsyncIOMotorGridFSBucket(self.db, bucket_name = base)

        try:
            grid_out = await storage.open_download_stream(id)
        except NoFile:
            abort(404)

        file_obj = await grid_out.read()
        mimetype = grid_out.metadata["contentType"]
        attachment_filename = grid_out.filename

        response = await send_file(
            file_obj,
            mimetype=mimetype,
            attachment_filename=attachment_filename,
            cache_timeout=cache_for
        )

    async def save_file(
        self,
        filename: str,
        fileobj: SupportsRead[AnyStr],
        base: str = "fs",
        content_type: Optional[str] = None
        ) -> ObjectId:
        """
        Save a file like object to GridFS using the given filename.
        """
        if not isinstance(base, str):
            raise TypeError(GRIDFS_STRING)
        if not (hasattr(fileobj, "read") and callable(fileobj.read)):
            raise TypeError(GRIDFS_FILEOBJ)

        if content_type is None:
            content_type = mimetypes.guess_type(filename)[0]

        storage = AsyncIOMotorGridFSBucket(self.db, bucket_name = base)

        if isawaitable(fileobj.read()):
            data = await fileobj.read()
        else:
            data = fileobj.read()

        grid_in = storage.open_upload_stream(
            filename, metadata={"contentType": content_type}
        )
        await grid_in.write(data)
        await grid_in.close()
        return grid_in._id
