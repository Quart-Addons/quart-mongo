"""
quart_mongo.helpers.schema.validation
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import auto, Enum
from functools import wraps
from typing import Any, Callable, cast, Dict, Optional, Tuple, Type, TypeVar, Union

from humps import decamelize
from odmantic import Model as ODM_Model
from odmantic.exceptions import DocumentParsingError
from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic.schema import model_schema
from quart import current_app, request, ResponseReturnValue as QuartResponseReturnValue
from werkzeug.datastructures import Headers
from werkzeug.exceptions import BadRequest

from quart_mongo.typing import Model, PydanticModel, ResponseReturnValue

QUART_MONGO_REQUEST_ATTRIBUTE = "_quart_mongo_request_schema"
QUART_MONGO_RESPONSE_ATTRIBUTE = "_quart_mongo_response_schema"

class SchemaInvalidError(Exception):
    """
    Schema Invalid Error
    """

class ResponseSchemaValidationError(Exception):
    """
    Reponse Schema Validation Error
    """
    def __init__(self, validation_error: Optional[ValidationError] = None) -> None:
        self.validation_error = validation_error

class ResponseHeadersValidationError(ResponseSchemaValidationError):
    """
    Response Headers Validation Error
    """

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

def mongo_validate_request(
        model_class: ODM_Model,
        *,
        source: DataSource = DataSource.JSON
) -> Callable:
    """
    Validate the request data.

    This ensures that the request body is JSON and that the body
    can be converted to the *model_class*. If they cannot a
    `RequestSchemaValidationError` is raisted which by default 
    results in a 400 response.

    Arguments:
        model_class: The `Odmantic` model to use. All the fields
            must be optional..
        source: The source of the data validate (json or form
            encoded.)
    """
    """
    schema = model_schema(model_class)

    if source == DataSource.FORM and any(
        schema["properties"][field]["type"] == "object" for field in schema["properties"]
    ):
        raise SchemaInvalidError("Form must not have nested objects.")
    """
    def decorator(func: Callable) -> Callable:
        setattr(func, QUART_MONGO_REQUEST_ATTRIBUTE, (model_class, source))

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if source == DataSource.JSON:
                data = await request.get_json()
            else:
                data = await request.form()

            if current_app.config["QUART_MONGO_CONVERT_CASING"]:
                data = decamelize(data)

            try:
                model = model_class(**data)
            except (TypeError, ValidationError) as error:
                raise RequestSchemaValidationError(error)
            else:
                return await current_app.ensure_async(func)(*args, data=model, **kwargs)

        return wrapper

    return decorator

def mongo_validate_response(
        model_class: ODM_Model,
        status_code: int = 200,
        header_model_class: Optional[Model] = None
) -> Callable:
    """
    Validate the response data.

    This ensures that the response is either a dictionary that the body can be 
    converted to the *model_class* or an instance of the *model_class*. If this 
    is not possible a `ResponseSchemaValidationError` is raised which by default 
    results in a 500 response. The returned value is then a dictionary which 
    `Quart` can encodes as JSON.

    Arguments:
        model_class: The `Odmantic` model to use. 
        status_code: The status code this validation applies. Defaults to 200.
        header_model_class: The model to use to validate response headers, 
            either a dataclass, pydantic dataclass, or a class that inherits
            from pydantic's BaseModel. Is optional.
    """
    headers_model_class = _to_pydantic_model(header_model_class)

    def decorator(
            func: Callable[..., ResponseReturnValue]
    ) -> Callable[..., QuartResponseReturnValue]:
        schemas = getattr(func, QUART_MONGO_RESPONSE_ATTRIBUTE, {})
        schemas[status_code] = (model_class, headers_model_class)
        setattr(func, QUART_MONGO_RESPONSE_ATTRIBUTE, schemas)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await current_app.ensure_async(func)(*args, **kwargs)

            status_or_headers = None
            headers = None

            if isinstance(result, tuple):
                value, status_or_headers, headers = result + (None,) * (3 - len(result))
            else:
                value = result

            status = 200

            if isinstance(status_or_headers, int):
                status = int(status_or_headers)

            if status == status_code:
                try:
                    if isinstance(value, dict):
                        model_value = model_class(**value)
                    elif isinstance(value, model_class):
                        model_value = value
                    elif is_dataclass(value):
                        model_value = model_class(**asdict(value))
                    else:
                        raise ResponseSchemaValidationError
                except DocumentParsingError as error:
                    raise ResponseSchemaValidationError(error)

                if header_model_class is not None:
                    try:
                        if isinstance(headers, dict):
                            headers_model_value = _convert_headers(headers, headers_model_class)
                        elif isinstance(headers, header_model_class):
                            headers_model_value = headers
                        elif is_dataclass(headers):
                            headers_model_value = headers_model_class(**asdict(headers))
                        else:
                            raise ResponseHeadersValidationError()
                    except ValidationError as error:
                        raise ResponseHeadersValidationError(error)

                    if is_dataclass(headers_model_value):
                        headers_value = asdict(headers_model_value)
                    else:
                        headers_value = cast(BaseModel, headers_model_value).dict()
                else:
                    headers_value = headers

                return model_value, status, headers_value
            else:
                return result

        return wrapper

    return decorator

def mongo_validate(
        *,
        request: Optional[ODM_Model] = None,
        request_source: DataSource = DataSource.JSON,
        responses: Dict[int, Tuple[ODM_Model, Optional[Model]]]
) -> Callable:
    """
    Validate the route.

    This is a shorthand combination of the mongo_validate_request
    and mongo_validate_response decorators. Please see the docstrings
    for those decorators for more information.
    """
    def decorator(func: Callable) -> Callable:
        if request is not None:
            func = mongo_validate_request(request, source=request_source)(func)
        for status, models in responses.items():
            func = mongo_validate_response(models[0], status, models[2])
        return func

    return decorator

T = TypeVar("T")

def _convert_headers(
        headers: Union[dict, Headers],
        model_class: Type[T]
        ) -> T:
    """
    Converts headers.
    """
    result = {}

    for raw_key in headers.keys():
        key = raw_key.replace("-", "_").lower()
        if key in model_class.__annotations__:
            if isinstance(headers, Headers):
                result[key] = ",".join(headers.get_all(raw_key))
            else:
                result[key] = headers[raw_key]
    return model_class(**result)

def _to_pydantic_model(model_class: Model) -> PydanticModel:
    """
    Converts a model to a pydantic model.
    """
    pydantic_model_class: PydanticModel

    if is_dataclass(model_class):
        pydantic_model_class = pydantic_dataclass(model_class)
    else:
        pydantic_model_class = cast(PydanticModel, model_class)
    return pydantic_model_class