"""
quart_mongo.json

Provides JSON helpers for MongoDB.
"""
from typing import Any, Optional

from bson import json_util, SON
from bson.json_util import DEFAULT_JSON_OPTIONS, JSONOptions
from quart import Quart
from quart.json.provider import _default, DefaultJSONProvider
from six import iteritems, string_types

class MongoJSONProvider(DefaultJSONProvider):
    """
    A subclass of `quart.json.provider.DefaultJSONProvider`
    that can handle "MongoDB" type objects.
    """
    def __init__(self, app: Quart, json_options: Optional[JSONOptions] = None) -> None:
        """
        Constructs the JSON Provider Class.
        """
        if json_options is None:
            json_options = DEFAULT_JSON_OPTIONS

        if json_options is not None:
            self._default_kwargs = {"json_options": json_options}
        else:
            self._default_kwargs = {}

        super(DefaultJSONProvider).__init__(app)

    def default(self, object_: Any) -> Any:
        """
        Apply this function to any object that :meth:`json.dumps` does
        not know how to serialize. It should return a valid JSON type or
        raise a ``TypeError``.

        Arguments:
            object_: The object to dump.
        """
        if hasattr(object_, "iteritems") or hasattr(object_, "items"):
            return SON((k, self.default(v)) for k, v in iteritems(object_))
        elif hasattr(object_, "__iter__") and not isinstance(object_, string_types):
            return [self.default(v) for v in object_]
        else:
            try:
                return json_util.default(object_, **self._default_kwargs)
            except TypeError:
                # PyMongo couldn't convert into a serializable object, and
                # the Flask default JSONEncoder won't; so we return the
                # object itself and let stdlib json handle it if possible
                return _default(object_)
