"""
quart_mongo.extension
"""
from io import BytesIO
from mimetypes import guess_type
from typing import Any, BinaryIO, Optional

from bson import ObjectId
from gridfs import NoFile
from gridfs.asynchronous import AsyncGridFS
import pymongo
from quart import Quart, abort, Response

from quart_mongo.config import MongoConfig, register_helpers
from quart_mongo.helpers import GridFsFileWrapper, generate_etag, send_gridfs

from .wrappers import MongoClient, Database


DESCENDING = pymongo.DESCENDING
"""Descending sort order."""

ASCENDING = pymongo.ASCENDING
"""Ascending sort order."""


# pylint: disable=W1113


class PyMongo:
    """
    Manages MongoDB connections for your Quart app using `~pymongo`.

    PyMongo objects provide access to the MongoDB server via the :attr:`db`
    and :attr:`cx` attributes. You must either pass the :class:`~quart.Quart`
    app to the constructor, or call :meth:`init_app`.

    PyMongo accepts a MongoDB URI via the ``MONGO_URI`` Quart configuration
    variable, or as an argument to the constructor or ``init_app``. See
    :meth:`init_app` for more detail.

    Arguments:
        app: An instance of :class:`~quart.Quart`.
        uri: MongoDB uri with or without the databasename.
        args: Positional arguments for :class:`~MongoClient`.
        kwargs: Keyword arguments for :class:`~MongoClient`.
    """
    def __init__(
            self, app: Optional[Quart] = None,
            uri: Optional[str] = None,
            *args: Any,
            **kwargs: Any
    ) -> None:
        self.config: MongoConfig | None = None
        self.cx: MongoClient | None = None
        self.db: Database | None = None

        if app is not None:
            self.init_app(app, uri, *args, **kwargs)

    def init_app(
            self, app: Quart,
            uri: Optional[str] = None,
            *args: Any,
            **kwargs: Any
    ) -> None:
        """
        Initialize this :class:`Mongo` for use.

        Configure a :class:`~pymongo.mongo_client.MongoClient`
        in the following scenarios:

        1. If ``uri`` is not ``None``, pass the ``uri`` and any positional
           or keyword arguments to :class:`~pymongo.mongo_client.MongoClient`
        2. If ``uri`` is ``None``, and a Flask config variable named
           ``MONGO_URI`` exists, use that as the ``uri`` as above.

        The caller is responsible for ensuring that additional positional
        and keyword arguments result in a valid call.

        If the ``uri`` does not contain the database name, then the
        :attr:`db` will be ``None``.

        Arguments:
            app: An instance of :class:`~quart.Quart`.
            uri: MongoDB uri with or without the databasename.
            args: Positional arguments for :class:`~MongoClient`.
            kwargs: Keyword arguments for :class:`~MongoClient`.
        """
        self.config = MongoConfig(app, uri, *args, **kwargs)
        self.cx = MongoClient(*self.config.args, **self.config.kwargs)

        if self.config.database_name:
            self.db = self.cx[self.config.database_name]

        register_helpers(app)

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
        containing the named file, and implement conditional GET semantics
        (using :meth:`~werkzeug.wrappers.ETagResponseMixin.make_conditional`).

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

        storage = AsyncGridFS(db_obj, base)

        try:
            grid_out = await storage.get_version(
                filename=filename, version=version
                )
        except NoFile:
            abort(404)

        etag = await generate_etag(grid_out)

        raw = await grid_out.read()
        file = BytesIO(raw)

        return await send_gridfs(
            file,
            grid_out.length,
            mimetype=grid_out.content_type,
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

        if content_type is None:
            content_type, _ = guess_type(filename)

        if db and self.cx is not None:
            db_obj = self.cx[db]
        elif self.db is not None:
            db_obj = self.db
        else:
            db_obj = None

        assert db_obj is not None, "Please initialize the app before calling \
            save_file!"

        storage = AsyncGridFS(db_obj, base)

        # GridFS does not manage its own checksum, so we attach a sha1 to the
        # file for use as an etag.
        hashingfile = GridFsFileWrapper(fileobj)

        async with storage.new_file(
            filename=filename, content_type=content_type, **kwargs
        ) as grid_file:
            await grid_file.write(hashingfile)
            grid_file.sha1 = hashingfile.hash.hexdigest()
            return grid_file._id  # pylint: disable=W0212


__all__ = (
    "PyMongo",
    "ASCENDING",
    "DESCENDING"
)
