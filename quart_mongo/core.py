"""
quart_mongo.core

The extension for Quart Mongo.
"""
from __future__ import annotations
from mimetypes import guess_type
from typing import Any, AnyStr, Optional, TYPE_CHECKING

from bson import ObjectId
from gridfs import AsyncGridFS, NoFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pymongo import uri_parser
from quart import Quart, abort, current_app, Response, send_file, make_response

from .const import MONGO_URI_ERROR
from .helpers import BSONObjectIdConverter, MongoJSONProvider
from .wrappers import AIOMotorClient, AIOMotorDatabase, AIOEngine
from .typing import JSONOptions
from .utils import check_file_object, check_gridfs_arguments


if TYPE_CHECKING:
    from _typeshed import SupportsRead


class Mongo:
    """
    This class is for integrating MongoDB into your `Quart` application. It
    integrates with MongoDB by using `Motor` and `Odmantic`. It also provides
    a few helper functions for working with MongoDB.

    Arguments:
        app: The `Quart` application to use. Defaults to ``None``.
        uri: The MongoDB URI to use. This parameter defaults to ``None``
            and will then use the app config.
        json_options: Options for JSON encoding.
        args: Arguments to pass to `AIOMotorClient` on initialization.
        kwargs: Extra arguments to pass to `AIOMotorClient` on initialization.
    """
    def __init__(  # pylint: disable=W1113
            self,
            app: Optional[Quart] = None,
            uri: Optional[str] = None,
            json_options: Optional[JSONOptions] = None,
            *args: Any,
            **kwargs: Any
    ) -> None:
        self.json_options = json_options
        self.args: Optional[tuple] = None
        self.kwargs: Optional[dict] = None
        self.cx: AIOMotorClient = None
        self.db: AIOMotorDatabase = None
        self.odm: AIOEngine = None

        if app is not None:
            self.init_app(app, uri, *args, **kwargs)

    def init_app(  # pylint: disable=W1113
            self,
            app: Quart,
            uri: Optional[str] = None,
            *args: Any,
            **kwargs: Any
    ) -> None:
        """
        This function configures `Mongo` and applies the extension instance
        with the given application.

        It also will get the database name from the URI if it was provided,
        register the connection function with the app as a before serving
        function, and register BSON and JSON helpers with the app.

        Note that BSON and JSON helpers are only added to the app if they
        have not been. This is in case of multiple instances of this class.

        If you are using `quart_schema` in your application. Make sure you
        register `quart_schema with the application before this extension.
        This is so the JSON provider for this extension can be used with the
        application in lieu of the one with `quart_schema`.

        Parameters:
            app: The application to use.
            uri: The MongoDB URI to use. This parameter defaults to `None`
                and will then use the app config.
            json_options: Options for JSON encoding.
            args: Arguments to pass to `AIOMotorClient` on initialization.
            kwargs: Extra arguments to pass to `AIOMotorClient` on
                initialization.
        """
        app.config.setdefault("QUART_MONGO_JSON_OPTIONS", self.json_options)

        if uri is None:
            uri = app.config.get("MONGO_URI", None)

        if uri is not None:
            self.args = tuple([uri] + list(args))
        else:
            raise ValueError(MONGO_URI_ERROR)

        parsed_uri = uri_parser.parse_uri(uri)
        self.database = parsed_uri["database"]

        # Try to delay connecting, in case the app is loaded
        # before forking per:
        # https://pymongo.readthedocs.io/en/stable/faq.html#is-pymongo-fork-safe
        self.kwargs = kwargs
        self.kwargs['connect'] = False

        app.before_serving(self._connect_db)

        # Register helpers with the app.
        # This only needs to happen if they have not already been registered.
        # In case of multiple instance of this class.
        if "ObjectId" not in app.url_map.converters:
            app.url_map.converters["ObjectId"] = BSONObjectIdConverter

        if not isinstance(app.json, MongoJSONProvider):
            app.json = MongoJSONProvider(app)

    async def _connect_db(self) -> None:
        """
        Before Serving Function (Private)

        This function is registered with application with the
        :attr:`~Mongo.init_app` and is called by the application before
        serving any routes.

        The purpose of the function is to setup `AIOMotorClient` and also
        `AIOMotorDatabase` and `AIOEngine` if the MongoDB URI provides the
        database name.
        """
        self.cx = AIOMotorClient(*self.args, **self.kwargs)

        if self.database:
            self.db = self.cx.motor(self.database)
            self.odm = self.cx.odm(self.database)

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
            version: Which version of the file to retrieve.
                Defaults to -1 (most recent).
            int cache_for: Number of seconds that browsers should be
                instructed to cache responses
        """
        check_gridfs_arguments(
            base=base, version=version, cache_for=cache_for
        )

        storage = AsyncIOMotorGridFSBucket(self.db, bucket_name=base)

        try:
            grid_out = await storage.open_download_stream_by_name(
                filename, revision=version
            )
        except NoFile:
            abort(404)

        file = await grid_out.read()
        mimetype = grid_out.metadata.get("mimetype", None)
        response = await make_response(file)
        return response

    async def send_file_by_id(
            self,
            oid: ObjectId,  # pylint: disable=W0622
            base: str = "fs",
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
            oid: The bson Object id of the file.
            base: The base name of the GridFS collections to use
            version: If positive, return the Nth revision of the file
                identified by filename; if negative, return the Nth most recent
                revision. If no such version exists, return with HTTP status
                404.
            int cache_for: Number of seconds that browsers should be
                instructed to cache responses
        """
        if not isinstance(oid, ObjectId):
            raise TypeError("'oid' must be a `bson.ObjectId`")
        if not isinstance(base, str):
            raise TypeError("'base' must be a string")
        if not isinstance(cache_for, int):
            raise TypeError("'cache_for' must be an integer")

        storage = AsyncGridFS(self.db, base)  # type: ignore[arg-type]

        try:
            file_obj = await storage.get(oid)
        except NoFile:
            abort(404)

        return await send_file(
            file_obj,
            mimetype=file_obj.content_type,
            attachment_filename=file_obj.filename,
            add_etags=True,
            cache_timeout=cache_for,
            last_modified=file_obj.upload_date
        )

    async def save_file(
        self,
        filename: str,
        fileobj: SupportsRead[AnyStr],
        base: str = "fs",
        mimetype: Optional[str] = None,
        **kwargs: Any
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
            base: bucket name of the GridFS collections to use
            mimetype: the mimetype of the file. If
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
            metadata = dict()

        if mimetype is None:
            mimetype, _ = guess_type(filename)
            metadata['mimetype'] = mimetype

        storage = AsyncIOMotorGridFSBucket(self.db, bucket_name=base)

        oid = await storage.upload_from_stream(
            filename,
            fileobj,
            metadata=metadata
        )
        return oid
