"""
quart_mongo.config

Provides helper classes and functions for configuring
MongoDB with Quart-Mongo.
"""
import typing as t

from pydantic import BaseModel
from quart import Quart

from .const import MONGO_URI_ERROR

class MongoConfig(BaseModel):
    """
    Stores the Mongo Configuration for `quart_mongo.Mongo`.

    This is a subclass to `pydantic.BaseModel`.

    Arguments:
        uri: The MongoDB URI.
        database: The database name.
        args: arguments to pass to `AIOMotorClient`.
        kwargs: extra arguments to pass to `AIOMotorClient`.
    """
    uri: t.Optional[str]
    database: t.Optional[str]
    args: t.Optional[t.Tuple[t.Any]]
    kwargs: t.Optional[t.Dict[str, t.Any]]

def _get_uri(app: Quart, uri: t.Optional[str]) -> str:
    """
    Gets the MongoDB URI from the app configuration.

    If no MongoDB URI is found in the app configuration.
    This function will set the ``MONGO_URI`` configuration variable
    to ``None`` as default.

    This function is private and should not be called. It is called by
    `quart_mongo.Mongo` at creation time to get the MongoDB URI if one
    was not provided dirctly to it.

    Arguments:
        app: The `quart.Quart` application.
        uri: The MongoDB URI.

    Raises:
        `ValueError`: If no MongoDB URI is found in the app configuration.
    """
    if uri is None:
        uri = app.config.setdefault("MONGO_URI", None)

    if uri is not None:
        return uri
    else:
        raise ValueError(MONGO_URI_ERROR)
