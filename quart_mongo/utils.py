"""
quart_mongo.utils
"""
from __future__ import annotations
from typing import Any, AnyStr, Optional, TYPE_CHECKING

from motor.motor_asyncio import AsyncIOMotorGridOut
from quart import Response, send_file

from .const import (
    GRIDFS_FILEOBJ,
    GRIDFS_STRING,
    GRIDFS_VERSION,
    GRIDFS_CACHE
)

if TYPE_CHECKING:
    from _typeshed import SupportsRead


def check_file_object(fileobj: SupportsRead[AnyStr]) -> None:
    """
    Checks if a file object has a read method. If not raises
    a `TypeError`.
    """
    if not (hasattr(fileobj, "read") and callable(fileobj.read)):
        raise TypeError(GRIDFS_FILEOBJ)


def check_gridfs_arguments(
    check_base: bool = True,
    base: Optional[str] = None,
    check_version: bool = True,
    version: Optional[int] = None,
    check_cache_for: bool = True,
    cache_for: Optional[int] = None,
) -> None:
    """
    Check if GridFS arguments are the correct type. If not will raise a
    `TypeError`.
    """
    if check_base:
        if not isinstance(base, str):
            raise TypeError(GRIDFS_STRING)

    if check_version:
        if not isinstance(version, int):
            raise TypeError(GRIDFS_VERSION)

    if check_cache_for:
        if not isinstance(cache_for, int):
            raise TypeError(GRIDFS_CACHE)


async def create_response(
        grid_out: AsyncIOMotorGridOut,
        filename: Optional[str] = None,
        cache_timeout: int = 31536000
) -> Response:
    """
    Create as response using `Quart.send_file`.
    """
    file_obj: Any = await grid_out.read()
    mimetype = grid_out.metadata["contentType"]
    last_modified = grid_out.upload_date

    if filename is None:
        attachment_filename = grid_out.filename
    else:
        attachment_filename = filename

    return await send_file(
        file_obj,
        mimetype=mimetype,
        attachment_filename=attachment_filename,
        cache_timeout=cache_timeout,
        conditional=True,
        last_modified=last_modified
    )
