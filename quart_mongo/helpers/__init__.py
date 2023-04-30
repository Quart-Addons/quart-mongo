"""
quart_mongo.helpers

Helpers for Quart Mongo.
"""
from typing import Optional
from types import new_class

from bson.json_util import JSONOptions
from quart import Quart

from .bson import BSONObjectIdConverter
from .json import MongoJSONProvider

from .schema import (
    SchemaValidationError,
    WebsocketMixin,
    TestClientMixin,
    convert_model_result,
    RequestSchemaValidationError,
    ResponseSchemaValidationError,
    DataSource,
    mongo_validate_request,
    mongo_validate_response,
    mongo_validate
)

def register_mongo_helpers(
        app: Quart,
        bson: bool = True,
        json: bool = True,
        json_options: Optional[JSONOptions] = None,
        schema: bool = True,
        convert_casing: bool = True
) -> None:
    """
    Registers Mongo Helpers with the Quart Extension.

    This function will register the BSON URL converter,
    JSON Provider, and the schema helpers to be used 
    with Mongo.

    Note: This function should only be called once and does
    not need to be called for every `Mongo` instance. 

    Arguments:
        app: The `Quart app.
        bson: Determines if the BSON URL converter should be
            setup with the app. Defaults to ``True``.
        json: Dertermines if `MongoJSONProvider` class should
            be setup with the app. Defaults to ``True``.
        json_options: JSON Options for the `MongoJSONProvider`
            class. Defaults to ``None``.
        schema: Determines to setup the schema helpers with 
            the app. Defaults to ``True``.
        convert_casing: Determines to convert camel casing from
            javascript. This is used with schema. Defaults to
            ``True``.
    """
    # Setup configuration values
    app.config.setdefault("QUART_MONGO_BSON_CONVERTER", bson)
    app.config.setdefault("QUART_MONGO_JSON_PROVIDER", json)
    app.config.setdefault("QUART_MONGO_JSON_OPTIONS", json_options)
    app.config.setdefault("QUART_MONGO_SCHEMA", schema)
    app.config.setdefault("QUART_MONGO_CONVERT_CASING", convert_casing)

    # Register BSON URL Converter
    if app.config["QUART_MONGO_BSON_CONVERTER"]:
        app.url_map.converters["ObjectId"] = BSONObjectIdConverter

    # Register JSON Provider
    if app.config["QUART_MONGO_JSON_PROVIDER"]:
        app.json_provider_class = MongoJSONProvider
        app.json = app.json_provider_class(app)

    # Register Schema Helpers
    if app.config["QUART_MONGO_SCHEMA"]:
        app.test_client_class = new_class("TestClient", (TestClientMixin, app.test_client_class))
        app.websocket_class = new_class("Websocket", (WebsocketMixin, app.websocket_class))
        app.make_response = convert_model_result(app.make_response)

__all__ = (
    "register_mongo_helpers",
    "MongoJSONProvider",
    "SchemaValidationError",
    "RequestSchemaValidationError",
    "ResponseSchemaValidationError",
    "DataSource",
    "mongo_validate_request",
    "mongo_validate_response",
    "mongo_validate"
)
