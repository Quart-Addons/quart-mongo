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
from quart import Quart, abort, Response

from .config import MongoConfig, get_uri
from .helpers import BSONObjectIdConverter, MongoJSONProvider

from .utils import (
    check_file_object,
    check_gridfs_arguments,
    create_response
)

from .wrappers import AIOMotorClient, AIOMotorDatabase, AIOEngine
from .typing import JSONOptions

if TYPE_CHECKING:
    from _typeshed import SupportsRead
    from motor.motor_asyncio import AsyncIOMotorGridIn

class Mongo:
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
        The constructor of the Mongo class.

        Arguments:
            app: The `Quart` application to use. Defaults to ``None``.
            uri: The MongoDB URI to use. This parameter defaults to ``None``
            and will then use the app config.
            json_options: Options for JSON encoding.
            args: Arguments to pass to `AIOMotorClient` on intialization.
            kwargs: Extra agrugments to pass to `AIOMotorClient` on intialization.
        """
        self.config: Optional[MongoConfig] = None
        self.cx: Optional[AIOMotorClient] = None
        self.db: Optional[AIOMotorDatabase] = None
        self.odm: Optional[AIOEngine] = None

        if app is not None:
            self.init_app(app, uri, json_options, *args, **kwargs)

    def init_app(
            self,
            app: Quart,
            uri: Optional[str] = None,
            json_options: Optional[JSONOptions] = None,
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
        uri = get_uri(app, uri)
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
        app.before_serving(self._setup_db)

        # Register helpers with the app.
        # This only needs to happen if they have not already been registered.
        # In case of multiple instance of this class.
        if not "ObjectId" in app.url_map.converters:
            app.url_map.converters["ObjectId"] = BSONObjectIdConverter

        if not isinstance(app.json, MongoJSONProvider):
            app.json = MongoJSONProvider(app)

    async def _setup_db(self) -> None:
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

    async def send_file_by_name(
        self,
        filename: str,
        base: str = "fs",
        version: int = -1,
        cache_for: int = 31536000
        ) -> Response:
        """
        Respond with a file from GridFS using the file name.

        Returns an instance of the :attr:`~quart.Quart.response_class`
        containing the named file, and implement conditional GET semantics.

        .. code-block:: python

            @app.route("/uploads/<path:filename>")
            async def get_upload(filename):
                return await mongo.send_file_by_name(filename)

        Arguments:
            filename: The filename of the file to return
            base: The base name of the GridFS collections to use
            version: If positive, return the Nth revision of the file
                identified by filename; if negative, return the Nth most recent
                revision. If no such version exists, return with HTTP status 404.
            int cache_for: Number of seconds that browsers should be
                instructed to cache responses
        """
        check_gridfs_arguments(base=base, version=version, cache_for=cache_for)

        storage = AsyncIOMotorGridFSBucket(self.db, bucket_name = base)

        try:
            grid_out = await storage.open_download_stream_by_name(filename, version)
        except NoFile:
            abort(404)

        return await create_response(
            grid_out, filename=filename, cache_timeout=cache_for
        )

    async def send_file_by_id(
            self,
            id: ObjectId,
            base: str = "fs",
            version: int = -1,
            cache_for: int = 31536000
            ) -> Response:
        """
        Respond with a file from GridFS using the file Object id.

        Returns an instance of the :attr:`~quart.Quart.response_class`
        containing the named file, and implement conditional GET semantics.

        .. code-block:: python

            @app.route("/uploads/<str:id>")
            async def get_upload(id):
                return await mongo.send_file_by_id(id)

        Arguments:
            id: The bson Object id of the file.
            base: The base name of the GridFS collections to use
            version: If positive, return the Nth revision of the file
                identified by filename; if negative, return the Nth most recent
                revision. If no such version exists, return with HTTP status 404.
            int cache_for: Number of seconds that browsers should be
                instructed to cache responses
        """
        check_gridfs_arguments(base=base, version=version, cache_for=cache_for)

        storage = AsyncIOMotorGridFSBucket(self.db, bucket_name = base)

        try:
            grid_out = await storage.open_download_stream(id)
        except NoFile:
            abort(404)

        return await create_response(grid_out, cache_timeout=cache_for)

    async def save_file(
        self,
        filename: str,
        fileobj: SupportsRead[AnyStr],
        base: str = "fs",
        content_type: Optional[str] = None,
        **kwargs
        ) -> ObjectId:
        """
        Save a file-like object to GridFS using the given filename.

        .. code-block:: python

            @app.route("/uploads/<path:filename>", methods=["POST"])
            async def save_upload(filename):
                await mongo.save_file(filename, request.files["file"])
                return redirect(url_for("get_upload", filename=filename))

        Arguments:
            filename: the filename of the file to return
            file fileobj: the file-like object to save
            base: base the base name of the GridFS collections to use
            content_type: the MIME content-type of the file. If
                ``None``, the content-type is guessed from the filename using
                :func:`~mimetypes.guess_type`
            kwargs: extra attributes to be stored in the file's document,
            passed directly to :meth:`gridfs.GridFS.put`
        """
        check_gridfs_arguments(
            check_base=True,
            base=base,
            check_version=False,
            check_cache_for=False
        )

        check_file_object(fileobj)

        if kwargs:
            metadata = kwargs.copy()
        else:
            metadata = {}

        content_type = metadata.setdefault('contentType', content_type)

        if content_type is None:
            metadata['contentType'] = mimetypes.guess_type(filename)[0]

        storage = AsyncIOMotorGridFSBucket(self.db, bucket_name = base)

        if isawaitable(fileobj.read()):
            data = await fileobj.read()
        else:
            data = fileobj.read()

        grid_in = storage.open_upload_stream(filename, metadata=metadata)

        await grid_in.write(data)
        await grid_in.close()
        return grid_in._id
