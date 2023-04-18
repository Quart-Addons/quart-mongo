"""
quart_mongo

Mongo DB extension for Quart.
"""
from .const import ASCENDING, DESCENDING
from .core import Mongo
from .helpers import register_odmantic_schema
from .json import MongoJSONProvider
from .mixins import SchemaValidationError
from .typing import ResponseReturnValue
from .validation import (
    RequestSchemaValidationError,
    ResponseSchemaValidationError,
    mongo_validate_request,
    mongo_validate_response,
    mongo_validate
)

__all__ = (
    "ASCENDING",
    "DESCENDING",
    "Mongo",
    "register_odmantic_schema",
    "MongoJSONProvider",
    "SchemaValidationError",
    "ResponseReturnValue",
    "RequestSchemaValidationError",
    "ResponseSchemaValidationError",
    "mongo_validate_request",
    "mongo_validate_response",
    "mongo_validate"
)
