"""
quart_mongo.odm_models.validation
"""
from enum import auto, Enum
from functools import wraps
import typing as t

from humps import decamelize
from odmantic import Model
from pydantic import ValidationError
from pydantic.schema import model_schema
from quart import current_app, request, ResponseReturnValue as QuartResponseReturnValue
from werkzeug.exceptions import BadRequest

QUART_MONGO_REQUEST_ATTRIBUTE = "_quart_mongo_request_schema"
QUART_MONGO_RESPONSE_ATTRIBUTE = "_quart_mongo_response_schema"

class SchemaInvalidError(Exception):
    """
    Schema Invalid Error
    """
    pass

class ResponseSchemaValidationError(Exception):
    """
    Reponse Schema Validation Error
    """
    def __init__(self, validation_error: t.Optional[ValidationError] = None) -> None:
        self.validation_error = validation_error

class RequestSchemaValidationError(BadRequest):
    """
    Request Schema Validation Error
    """

class DataSource(Enum):
    """
    Datasource Enum.
    """
    FORM = auto()
    JSON = auto()

def mongo_validate_request() -> t.Callable:
    """
    Validate the request data.
    """
    pass

def mongo_validate_response() -> t.Callable:
    """
    Validate the response data.
    """
    pass

def mongo_validate() -> t.Callable:
    """
    Validate the route.
    """
    pass
