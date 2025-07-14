"""
quart_mongo.helpers
"""
from datetime import datetime, timedelta, timezone
import hashlib
from io import BytesIO
from mimetypes import guess_type
import warnings
from typing import BinaryIO

from gridfs.asynchronous import AsyncGridOut
from motor.motor_asyncio import AsyncIOMotorGridOut
from quart import current_app, request, Response
from quart.helpers import DEFAULT_MIMETYPE
from quart.wrappers.response import ResponseBody


class GridFsFileWrapper:
    """
    GridFS File Wrapper to include sha1 for etag.

    This is used since GridFS doesn't manage its own checksum.

    Arguments:
        file: The file to use.
    """
    def __init__(self, file: BinaryIO) -> None:
        self.file = file
        self.hash = hashlib.sha1()

    def read(self, n: int) -> bytes:
        """
        Reads the file and updates the hash.

        Arguments:
            n: The number of bytes to read.
        """
        data = self.file.read(n)
        if data:
            self.hash.update(data)
        return data


async def generate_etag(grid_out: AsyncGridOut | AsyncIOMotorGridOut) -> str:
    """
    Generates etag for GridFS.

    GridFS does not manage its own checksum. Try to use a
    sha1 sum that we have added during saving the file. This
    function will fallback to a legacy md5 sum if it exists.
    Otherwise, compute the sha1 sum directly.

    Arguments:
        grid_out: An instance of `~gridfs.asynchronous.AsyncGridOut`
    """
    if isinstance(grid_out, AsyncIOMotorGridOut):
        if grid_out.metadata is not None:
            etag = grid_out.metadata.get("sha1")
        else:
            etag = None

        if etag is not None:
            return etag
        else:
            pos = grid_out.tell()
            raw = await grid_out.read()
            grid_out.seek(pos)
            return hashlib.sha1(raw).hexdigest()
    else:
        try:
            return grid_out.sha1
        except AttributeError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                etag = grid_out.md5
            if etag is None:
                pos = grid_out.tell()
                raw = await grid_out.read()
                await grid_out.seek(pos)
                return hashlib.sha1(raw).hexdigest()
            return etag


async def send_gridfs(
        file: BytesIO,
        content_length: int,
        mimetype: str | None = None,
        as_attachment: bool = False,
        attachment_filename: str | None = None,
        add_etags: bool = True,
        etag: str | None = None,
        cache_timeout: int | None = None,
        last_modified: datetime | None = None
) -> Response:
    """
    Return a Response to send a GridFS file.

    This is a copy of `~quart.helpers.send_file` with
    changes for GridFS.

    Arguments:
        file: The bytes to send from GridFS.
        content_length: The file content length from GridFS.
        mimetype: Mimetype to use, by default it will be guessed or
            revert to the DEFAULT_MIMETYPE.
        as_attachment: If true use the attachment filename in a
            Content-Disposition attachment header.
        attachment_filename: Name for the filename, if it differs
        add_etags: Set etags based on the filename, size and
            modification time.
        etag: The etag to add to the response.
        last_modified: Used to override the last modified value.
        cache_timeout: Time in seconds for the response to be cached.
    """
    file_body: ResponseBody
    file_body = current_app.response_class.io_body_class(file)

    if mimetype is None and attachment_filename is not None:
        mimetype = guess_type(attachment_filename)[0] or DEFAULT_MIMETYPE

    if mimetype is None:
        raise ValueError(
            "The mime type cannot be inferred, please set it manually via the"
            " mimetype argument."
        )

    response = current_app.response_class(file_body, mimetype=mimetype)
    response.content_length = content_length

    if as_attachment:
        response.headers.add(
            "Content-Disposition", "attachment", filename=attachment_filename
        )

    if last_modified is not None:
        response.last_modified = last_modified

    response.cache_control.public = True
    if cache_timeout is not None:
        response.cache_control.max_age = cache_timeout
        response.expires = \
            datetime.now(timezone.utc) + timedelta(seconds=cache_timeout)

    if add_etags and etag is not None:
        response.set_etag(etag)

    await response.make_conditional(
        request, accept_ranges=True, complete_length=file.getbuffer().nbytes
    )
    return response
