"""
quart_mongo.config

Provides helper classes and functions for configuring
MongoDB with Quart-Mongo.
"""
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel
from quart import Quart

from .const import MONGO_URI_ERROR

class MongoConfig(BaseModel):
    """
    Stores the Mongo Configuration for `quart_mongo.Mongo`.

    Arguments:
        uri: The MongoDB URI.
        database: The database name.
        args: arguments to pass to `AIOMotorClient`.
        kwargs: extra arguments to pass to `AIOMotorClient`.
    """
    uri: Optional[str]
    database: Optional[str]
    args: Optional[Tuple[Any]]
    kwargs: Optional[Dict[str, Any]]

def get_uri(app: Quart, uri: Optional[str]) -> str:
    """
    Gets the MongoDB URI from the app configuration.

    If no MongoDB URI is found in the app configuration.
    This function will set the ``MONGO_URI`` configuration variable
    to ``None`` as default.

    This function should not be called. It is called by
    `quart_mongo.Mongo` at creation time to get the MongoDB URI if one
    was not provided dirctly to it.

    Arguments:
        app: The `quart.Quart` application.
        uri: The MongoDB URI.

    Raises:
        `ValueError`: If no MongoDB URI is found in the app configuration.
    """
    if uri is None:
        uri: str = app.config.get("QUART_MONGO_URI", None)

    if uri is not None:
        return uri
    else:
        raise ValueError(MONGO_URI_ERROR)
