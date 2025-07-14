"""
quart_mongo.config
"""
from typing import Any, Dict, Optional, Tuple

from pymongo import uri_parser
from pymongo.driver_info import DriverInfo
from quart import Quart

from .bson import BSONObjectIdConverter, BSONProvider


# pylint: disable=W1113


__version__ = "0.1.3"


class MongoConfig:
    """
    Quart Mongo Configuration

    This class holds and generates MongoDB configuration.

    MongoConfig accepts a MongoDB URI via the ``MONGO_URI``
    Quart configuration variable, or as an argument to the constructor.

    Arguments:
        app: an isntance of `quart.Quart`
        uri: MongoDB URI. This defaults to ``None`` and
            then will use the app configuration.
        args: positional arguments for the MongoDB client
        kwargs: keyword arguments for the MOngoDB client
    """
    def __init__(
            self, app: Quart, uri: Optional[str] = None,
            *args: Any, **kwargs: Any
    ) -> None:
        if uri is None:
            uri = app.config.get("MONGO_URI", None)

        if uri is None:
            raise ValueError(
                "The uri must be specified or set on the app config \
                    using the config variable ``MONGO_URI``"
                )
        self._uri = uri
        self._args = args
        self._kwargs = kwargs

        self._db_name: Optional[str] = None

    @property
    def args(self) -> Tuple[Any, ...]:
        """
        Positional arguments for the MongoDB client.
        """
        return tuple([self._uri] + list(self._args))

    @property
    def kwargs(self) -> Dict[str, Any]:
        """
        Keyword arguments for the MongoDB client.

        This will set to delay connecting to MongoDB in
        case the app is loaded before forking. Refer to
        https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/mongoclient/#forking-a-process-causes-a-deadlock

        Also, this will provided the driver info.
        """
        self._kwargs.setdefault("connect", False)

        if DriverInfo is not None:
            self._kwargs.setdefault(
                "driver", DriverInfo("Quart-Mongo", __version__)
                )

        return self._kwargs

    @property
    def parsed_uri(self) -> Dict[str, Any]:
        """
        Parsed MongoDB uri
        """
        return uri_parser.parse_uri(self._uri)

    @property
    def database_name(self) -> Optional[str]:
        """
        The database name from the parsed uri.
        It will return ``None`` if none was
        provided.
        """
        if self._db_name is None:
            self._db_name = self.parsed_uri.get("database")
        return self._db_name

    @database_name.setter
    def database_name(self, value: str) -> None:
        self._db_name = value


def register_helpers(app: Quart) -> None:
    """
    Configures the BSON ObjectID converter
    and BSON Provided with the app.
    """
    if "ObjectId" not in app.url_map.converters:
        app.url_map.converters["ObjectId"] = BSONObjectIdConverter

    if not isinstance(app.json, BSONProvider):
        app.json = BSONProvider(app)


__all__ = (
    "MongoConfig",
    "register_helpers"
)
