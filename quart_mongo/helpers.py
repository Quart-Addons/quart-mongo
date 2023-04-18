"""
quart_mongo.helpers

Provides helpers to the extension.
"""
from typing import Optional
from types import new_class

from bson.json_util import JSONOptions
from quart import Quart

from .bson import BSONObjectIdConverter
from .json import MongoJSONProvider
from .mixins import WebsocketMixin, TestClientMixin
from .response import convert_model_result

def register_mongo_helpers(
        app: Quart, json_options: Optional[JSONOptions] = None
) -> None:
    """
    Registers the BSON URL converter & Mongo
    JSON Provider with the `Quart` app.

    Arguments:
        app: The `Quart` application.
        json_options: The JSON Options for Mongo.
    """
    app.config.setdefault("QUART_MONGO_BSON_CONVERTER", True)
    app.config.setdefault("QUART_MONGO_JSON_PROVIDER", True)
    app.config.setdefault("QUART_MONGO_JSON_OPTIONS", json_options)

    if app.config["QUART_MONGO_BSON_CONVERTER"] and \
        "ObjectId" not in app.url_map.converters:
        app.url_map.converters["ObjectId"] = BSONObjectIdConverter

    if app.config["QUART_MONGO_JSON_PROVIDER"] and \
        not isinstance(app.json, MongoJSONProvider):
        app.json_provider_class = MongoJSONProvider
        app.json = app.json_provider_class(app)

def register_odmantic_schema(app: Quart, convert_casing: bool = True) -> None:
    """
    Registers `Odmantic` Schema helpers for sending and recieving `Odmantic.Models`
    with JSON.

    It will add a `TestClientMixin`, `WebsocketMixin`, and a `convert_model_result`
    response function. 

    These are not added when calling `Mongo.init_app` function, so the `Mongo` class
    can be used for multiple databases.

    Arguments:
        app: The `Quart` application.
        convert_casing: If camel casing is used or not.
    """
    app.config.setdefault("QUART_MONGO_CONVERT_CASING", convert_casing)

    app.test_client_class = new_class("TestClient", (TestClientMixin, app.test_client_class))
    app.websocket_class = new_class("Websocket", (WebsocketMixin, app.websocket_class))
    app.make_response = convert_model_result(app.make_response)
