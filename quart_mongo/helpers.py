"""
quart_mongo.helpers
"""
from typing import Any, Optional

from bson import json_util, SON
from bson.errors import InvalidId
from bson.json_util import DEFAULT_JSON_OPTIONS
from bson.objectid import ObjectId
from pydantic_core import to_jsonable_python
from quart import abort, Quart
from quart.json.provider import DefaultJSONProvider
from six import iteritems, string_types
from werkzeug.routing import BaseConverter

from .typing import JSONOptions


class BSONObjectIdConverter(BaseConverter):
    """
    A simple converter for the RESTful URL routing system of Quart.

    .. code-block:: python
        @app.route("/<ObjectId:task_id>")
        async def show_task(task_id):
            task = await mongo.db.tasks.find_one_or_404(task_id)
            return await render_template("task.html", task=task)

    Valid object ID strings are converted into :class:`bson.objectid.ObjectId`
    objects; invalid strings result in a 404 error.

    The converter is automatically registered by the initialization of
    :class:`~quart_mongo.Mongo` with keyword :attr:`ObjectId`.

    The :class:`~quart_mongo.helpers.BSONObjectIdConverter`
    is automatically installed on the
    :class:`~quart_mongo.Mongo` instance at creation
    time.
    """
    def to_python(self, value: str) -> ObjectId:
        """
        Converts a string value to an `ObjectId`.

        Parameters:
            value: The value to convert.

        Raises:
            `HTTPException`: Uses `quart.abort` to raise this exception
            if an ``InvaildId`` is raised by `ObjectId` with a 404 error code.
        """
        try:
            return ObjectId(value)
        except InvalidId:
            abort(404)

    def to_url(self, value: Any) -> str:
        """
        Converts a value to a URL string.
        """
        return str(value)


class MongoJSONProvider(DefaultJSONProvider):
    """
    A subclass of `quart.json.provider.DefaultJSONProvider`
    that can handle MongoDB type objects and Odmantic
    Model classes. It can also handle Pydantic type
    models as well, which is for `quart_schema`.
    """
    def __init__(self, app: Quart) -> None:
        json_options: Optional[JSONOptions] = \
            app.config.get("QUART_MONGO_JSON_OPTIONS", None)

        if json_options is None:
            json_options = DEFAULT_JSON_OPTIONS
        self._default_kwargs = {"json_options": json_options}

        super().__init__(app)

    def mongo_json(self, object_: Any) -> Any:
        """
        Handles JSON serialization for MongoDB.
        """
        if hasattr(object_, "iteritems") or hasattr(object_, "items"):
            return SON((k, self.default(v)) for k, v in iteritems(object_))
        elif hasattr(object_, "__iter__") and \
                not isinstance(object_, string_types):
            return [self.default(v) for v in object_]
        else:
            return json_util.default(object_, **self._default_kwargs)

    def default(self, object_: Any) -> Any:
        """
        Serialize MongoDB objects and pydantic types as well as the
        defaults.
        """
        try:
            return super().default(object_)
        except TypeError:
            try:
                return self.mongo_json(object_)
            except TypeError:
                return to_jsonable_python(object_)
