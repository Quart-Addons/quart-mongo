"""
quart_mongo.motor
"""
from __future__ import annotations

from io import BytesIO
from mimetypes import guess_type
from typing import Any, BinaryIO, Optional

from bson import ObjectId
from gridfs import NoFile
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from quart import Quart, abort, Response

from quart_mongo.config import MongoConfig, register_helpers
from quart_mongo.helpers import GridFsFileWrapper, generate_etag, send_gridfs

from .wrappers import AsyncIOMotorClient, AsyncIOMotorDatabase


# pylint: disable=W1113


class Motor:
    """
    Manages MongoDB connections for your Quart app using `~motor`.

    Motor objects provide access to the MongoDB server via the :attr:`db`
    and :attr:`cx` attributes. You must either pass the :class:`~quart.Quart`
    app to the constructor, or call :meth:`init_app`.

    Motor accepts a MongoDB URI via the ``MONGO_URI`` Quart configuration
    variable, or as an argument to the constructor or ``init_app``. See
    :meth:`init_app` for more detail.

    Arguments:
        app: An instance of :class:`~quart.Quart`.
        uri: MongoDB uri with or without the databasename.
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
        self.config: MongoConfig | None = None
        self.cx: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

        if app is not None:
            self.init_app(app, uri, *args, **kwargs)

    def init_app(
            self, app: Quart,
            uri: Optional[str] = None,
            *args: Any,
            **kwargs: Any
    ) -> None:
        """
        Initialize this :class:`Motor` for use.

        Configure a :class:`~motor_async.AsyncIOMotorClient`
        in the following scenarios:

        1. If ``uri`` is not ``None``, pass the ``uri`` and any positional
           or keyword arguments to :class:`~pymongo.mongo_client.MongoClient`
        2. If ``uri`` is ``None``, and a Flask config variable named
           ``MONGO_URI`` exists, use that as the ``uri`` as above.

        The caller is responsible for ensuring that additional positional
        and keyword arguments result in a valid call.

        If the ``uri`` does not contain the database name, then the
        :attr:`db` will be ``None`` and will need to set it yourself.

        Arguments:
            app: An instance of :class:`~quart.Quart`.
            uri: MongoDB uri with or without the databasename.
            args: Positional arguments for :class:`~AsyncIOMotorClient`.
            kwargs: Keyword arguments for :class:`~AsyncIOMotorClient`.
        """
        self.config = MongoConfig(app, uri, *args, **kwargs)
        app.before_serving(self._before_serving)
        register_helpers(app)

    async def _before_serving(self) -> None:
        """
        Before Serving Function (Private)

        This function is registered with application with the
        :attr:`~Motor.init_app` and is called by the application before
        serving any routes.

        The purpose of the function is to setup `AsyncIOMotorClient` and also
        `AsyncIOMotorDatabase` if the MongoDB URI provides the
        database name.
        """
        if self.config is None:
            raise ValueError("MongoDB Config for Motor is ``None``")

        self.cx = AsyncIOMotorClient(*self.config.args, **self.config.kwargs)

        if self.config.database_name:
            self.db = self.cx[self.config.database_name]

    async def send_file(
            self,
            filename: str,
            base: str = "fs",
            version: int = -1,
            cache_for: int = 31536000,
            db: Optional[str] = None
    ) -> Response:
        """
        Respond with a file from GridFS.

        Returns an instance of the :attr:`~quart.Quart.response_class`
        containing the named file, and implement conditional GET semantics.

        .. code-block:: python

            @app.route("/uploads/<path:filename>")
            async def get_upload(filename):
                return await mongo.send_file(filename)

        :param str filename: the filename of the file to return
        :param str base: the base name of the GridFS collections to use
        :param bool version: if positive, return the Nth revision of the file
           identified by filename; if negative, return the Nth most recent
           revision. If no such version exists, return with HTTP status 404.
        :param int cache_for: number of seconds that browsers should be
           instructed to cache responses
        :param str db: the target database, if different from the default
            database.
        """
        if not isinstance(base, str):
            raise TypeError("'base' must be string or unicode")
        if not isinstance(version, int):
            raise TypeError("'version' must be an integer")
        if not isinstance(cache_for, int):
            raise TypeError("'cache_for' must be an integer")

        if db and self.cx is not None:
            db_obj = self.cx[db]
        elif self.db is not None:
            db_obj = self.db
        else:
            db_obj = None

        assert db_obj is not None, "Please initialize the app before calling \
            send_file!"

        storage = AsyncIOMotorGridFSBucket(db_obj, base)

        try:
            grid_out = await storage.open_download_stream_by_name(
                filename, revision=version
            )
        except NoFile:
            abort(404)

        etag = await generate_etag(grid_out)

        if grid_out.metadata:
            content_type = grid_out.metadata.get("content_type", None)
        else:
            content_type = None

        raw: bytes = await grid_out.read()
        file = BytesIO(raw)

        return await send_gridfs(
            file,
            grid_out.length,
            mimetype=content_type,
            as_attachment=True,
            attachment_filename=grid_out.filename,
            add_etags=True,
            etag=etag,
            cache_timeout=cache_for,
            last_modified=grid_out.upload_date
            )

    async def save_file(
            self,
            filename: str,
            fileobj: BinaryIO,
            base: str = "fs",
            content_type: Optional[str] = None,
            db: Optional[str] = None,
            **kwargs: Any
    ) -> ObjectId:
        """
        Save a file-like object to GridFS using the given filename.
        Return the "_id" of the created file.

        .. code-block:: python

            @app.route("/uploads/<path:filename>", methods=["POST"])
            async def save_upload(filename):
                await mongo.save_file(filename, request.files["file"])
                return redirect(url_for("get_upload", filename=filename))

        :param str filename: the filename of the file to return
        :param file fileobj: the file-like object to save
        :param str base: base the base name of the GridFS collections to use
        :param str content_type: the MIME content-type of the file. If
           ``None``, the content-type is guessed from the filename using
           :func:`~mimetypes.guess_type`
        :param str db: the target database, if different from the default
            database.
        :param kwargs: extra attributes to be stored in the file's document,
           passed directly to :meth:`gridfs.GridFS.put`
        """
        if not isinstance(base, str):
            raise TypeError("'base' must be a string or unicode")
        if not (hasattr(fileobj, "read") and callable(fileobj.read)):
            raise TypeError("'fileobj' must have read() method")

        if kwargs:
            metadata = kwargs.copy()
        else:
            metadata = dict()

        if content_type is None:
            content_type, _ = guess_type(filename)
            metadata["content_type"] = content_type
        else:
            metadata["content_type"] = content_type

        if db and self.cx is not None:
            db_obj = self.cx[db]
        elif self.db is not None:
            db_obj = self.db
        else:
            db_obj = None

        assert db_obj is not None, "Please initialize the app before calling \
            save_file!"

        storage = AsyncIOMotorGridFSBucket(db_obj, base)

        # GridFS does not manage its own checksum, so we attach a sha1 to the
        # file for use as an etag.
        hashingfile = GridFsFileWrapper(fileobj)

        async with storage.open_upload_stream(
            filename, metadata=metadata
                ) as grid_in:
            await grid_in.write(hashingfile)
            await grid_in.set("sha1", hashingfile.hash.hexdigest())
            oid = grid_in._id  # pylint: disable=W0212
            await grid_in.close()

        return oid
