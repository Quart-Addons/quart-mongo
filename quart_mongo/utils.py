"""
quart_mongo.utils
"""
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

from humps import camelize
from odmantic import Model
from pydantic import BaseModel
from quart import Quart, current_app, Response, ResponseReturnValue

from .const import MONGO_URI_ERROR

def get_uri(app: Quart, uri: Optional[str] = None) -> str:
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
    uri: Optional[str]
    database: Optional[str]
    args: Optional[Tuple[Any]]
    kwargs: Optional[Dict[str, Any]]

def convert_odm_model_result(func: Callable) -> Callable:
    """
    Converts `odmantic.Model` to a dictionary to be used in a response.
    """
    @wraps(func)
    async def decorator(result: ResponseReturnValue) -> Response:
        status_or_headers = None
        headers = None

        if isinstance(result, tuple):
            value, status_or_headers, headers = result + (None,) * (3 - len(result))
        else:
            value = result

        was_model = False

        if isinstance(value, Model):
            dict_or_value = value.dict(by_alias=current_app.config["QUART_MONGO_BY_ALIAS"])
            was_model = True
        else:
            dict_or_value = value

        if was_model and current_app.config["QUART_MONGO_CONVERT_CASING"]:
            dict_or_value = camelize(dict_or_value)

        return await func((dict_or_value, status_or_headers, headers))
    return decorator
