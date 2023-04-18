"""
quart_mongo.json

Provides JSON Provider for MongoDB.
"""
from typing import Any

from bson import json_util, SON
from bson.json_util import DEFAULT_JSON_OPTIONS, JSONOptions
from quart import Quart
from quart.json.provider import _default, DefaultJSONProvider
from six import iteritems, string_types

class MongoJSONProvider(DefaultJSONProvider):
    """
    A subclass of `quart.json.provider.DefaultJSONProvider`
    that can handle MongoDB type objects.
    """
    def __init__(self, app: Quart) -> None:
        json_options: JSONOptions | None = app.config["QUART_MONGO_JSON_OPTIONS"]

        if json_options is None:
            json_options = DEFAULT_JSON_OPTIONS
        if json_options is not None:
            self._default_kwargs = {"json_options": json_options}
        else:
            self._default_kwargs = {}

        super(DefaultJSONProvider, self).__init__(app)

    def default(self, object_: Any) -> Any:
        """
        Serialize MongoDB object types using :mod:`bson.json_util`.

        if a `TypeError` is raised will retirn `quart.json.provider._default`.
        """
        if hasattr(object_, "iteritems") or hasattr(object_, "items"):
            return SON((k, self.default(v)) for k, v in iteritems(object_))
        elif hasattr(object_, "__iter__") and not isinstance(object_, string_types):
            return [self.default(v) for v in object_]
        else:
            try:
                json_util.default(object_, **self._default_kwargs)
            except TypeError:
                return _default(object_)
