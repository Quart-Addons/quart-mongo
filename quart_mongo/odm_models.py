"""
quart_mongo.odm_models

Provides helpers to `Quart` when working
with `odmantic` models.
"""
from enum import auto, Enum
from functools import wraps
import typing as t

from humps import decamelize
from odmantic import Model
from pydantic import ValidationError
from pydantic.schema import model_schema
from quart import current_app, request
from werkzeug.exceptions import BadRequest

QUART_MONGO_REQUEST_ATTRIBUTE = "_quart_mongo_request_schema"

class SchemaInvalidError(Exception):
    """
    Schema Invalid Error.
    """
    pass

class RequestSchemaValidationError(BadRequest):
    """
    Request Schema Validation Error.
    """
    def __init__(self, validation_error: t.Union[TypeError, ValidationError]) -> None:
        super().__init__()
        self.validation_error = validation_error

class DataSource(Enum):
    """
    Data Source Enum.
    """
    FORM = auto()
    JSON = auto()

def odm_validate_request(
        model_class: Model,
        *,
        source: DataSource = DataSource.JSON
        ) -> t.Callable:
    """
    some text
    """
    schema = model_schema(model_class)

    if source == DataSource.FORM and any(
        schema["properties"][field]["type"] == "object" for field in schema["properties"]
    ):
        raise SchemaInvalidError("Form must not have nested objects.")

    def decorator(func: t.Callable) -> t.Callable:
        setattr(func, QUART_MONGO_REQUEST_ATTRIBUTE, (model_class, source))

        @wraps(func)
        async def wrapper(*args: t.Any, **kwargs: t.Any):
            if source == DataSource.JSON:
                data = await request.get_json()
            else:
                data = await request.form()

            if current_app.config["QUART_MONGO_CASTING"]:
                data = decamelize(data)

            try:
                model = model_class(**data)
            except (TypeError, ValidationError) as error:
                raise RequestSchemaValidationError(error)
            else:
                return await current_app.ensure_async(func)(*args, data=model, **kwargs)

        return wrapper
    return decorator
