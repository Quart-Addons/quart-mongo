"""
quart_mongo.helpers.bson

Provides BSON url converter for Quart.
"""
from typing import Any

from bson.errors import InvalidId
from bson.objectid import ObjectId
from quart import abort
from werkzeug.routing import BaseConverter

class BSONObjectIdConverter(BaseConverter):
    """
    A simple converter for the RESTful URL routing system of Quart.

    .. code-block:: python
        @app.route("/<ObjectId:task_id>")
        async def show_task(task_id):
            task = await mongo.db.tasks.find_one_or_404(task_id)
            return await render_template("task.html", task=task)

    Valid object ID strings are converted into :class:`bson.objectid.ObjectId`
    objects; invalid strings result in a 404 error. The converter is automatically
    registered by the initialization of :class:`~quart_mongo.Mongo` with keyword
    :attr:`ObjectId`. The :class:`~quart_mongo.helpers.BSONObjectIdConverter` is
    automatically installed on the :class:`~quart_mongo.Mongo` instance at creation
    time.
    """
    def to_python(self, value: str) -> ObjectId:
        """
        Converts a string value to an `ObjectId`.

        Parameters:
            value (``str``): The value to convert.

        Returns:
            `ObjectId`: Returns this object if passed a vaild id.

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
