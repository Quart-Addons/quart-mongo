"""
quart_mongo.bson
"""
from typing import Any

from bson import json_util
from bson.errors import InvalidId
from bson.json_util import DEFAULT_JSON_OPTIONS
from bson.objectid import ObjectId
from quart import Quart, abort
from quart.json.provider import DefaultJSONProvider
from werkzeug.routing import BaseConverter


try:
    from pydantic_core import to_jsonable_python
except ImportError:
    to_jsonable_python = None


class BSONObjectIdConverter(BaseConverter):
    """A simple converter for the RESTful URL routing system of Quart.

    .. code-block:: python

        @app.route("/<ObjectId:task_id>")
        async def show_task(task_id):
            task = await mongo.db.tasks.find_one_or_404(task_id)
            return await render_template("task.html", task=task)

    Valid object ID strings are converted into
    :class:`~bson.objectid.ObjectId` objects; invalid strings result
    in a 404 error. The converter is automatically registered by the
    initialization of :class:`~quart_mongo.PyMongo` with keyword
    :attr:`ObjectId`.

    The :class:`~quart_mongo.helpers.BSONObjectIdConverter` is
    automatically installed on the :class:`~quart_mongo.PyMongo`
    instance at creation time.

    """

    def to_python(self, value: Any) -> ObjectId:
        try:
            return ObjectId(value)
        except InvalidId:
            abort(404)

    def to_url(self, value: Any) -> str:
        return str(value)


class BSONProvider(DefaultJSONProvider):
    """A JSON provider that uses :mod:`bson.json_util` for MongoDB documents.

    .. code-block:: python

        @app.route("/cart/<ObjectId:cart_id>")
        async def json_route(cart_id):
            results = mongo.db.carts.find({"_id": cart_id})
            return jsonify(results)


        # returns a Response with JSON body and application/json content-type:
        # '[{"count":12,"item":"egg"},{"count":1,"item":"apple"}]'

    Since this uses PyMongo's JSON tools, certain types may serialize
    differently than you expect. See :class:`~bson.json_util.JSONOptions`
    for details on the particular serialization that will be used.

    A :class:`~quart_mongo.helpers.JSONProvider` is automatically
    automatically installed on the :class:`~quart_mongo.Mongo`
    instance at creation time, using
    :const:`~bson.json_util.RELAXED_JSON_OPTIONS`.

    This provider will also dump `pydantic.Models` for
    when using `quart_schema` to validate the request and response
    of `beanie` document models. Make sure that you set the configuration
    variable ``MONGO_PYDANTIC_CONVERSION` to ``True`` if you need this
    functionality in your app. Also, make sure that you initialize
    `quart_mongo.PyMongo` after `quart_schema.QuartSchema`, so the
    correct JSON provider is added to the app.
    """

    def __init__(self, app: Quart) -> None:
        self._default_kwargs = {"json_options": DEFAULT_JSON_OPTIONS}
        super().__init__(app)

    @staticmethod
    def default(obj: Any) -> Any:
        """
        Default dumps
        """
        try:
            return super().default(obj)
        except ValueError:
            if to_jsonable_python is not None:
                return to_jsonable_python(obj)
            else:
                raise

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        """Serialize MongoDB object types using :mod:`bson.json_util`."""
        kwargs.setdefault("default", self.default)
        kwargs.setdefault("ensure_ascii", self.ensure_ascii)
        kwargs.setdefault("sort_keys", self.sort_keys)
        return json_util.dumps(obj, **kwargs)

    def loads(self, s: str | bytes, **kwargs: Any) -> Any:
        """Deserialize MongoDB object types using :mod:`bson.json_util`."""
        return json_util.loads(s, **kwargs)


__all__ = (
    "BSONObjectIdConverter",
    "BSONProvider"
)
