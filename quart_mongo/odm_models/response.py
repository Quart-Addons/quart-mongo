"""
quart_mongo.odm_models.response
"""
import typing as t
from functools import wraps

from humps import decamelize
from odmantic import Model
from quart import current_app, Response, ResponseReturnValue

def convert_model_result(func: t.Callable) -> t.Callable:
    """
    Converts a model for response result.
    """
    @wraps(func)
    async def decorator(result: ResponseReturnValue) -> Response:
        status_or_headers = None
        headers = None

        if isinstance(result, tuple):
            value, status_or_headers, headers = result + (None,) * (3 - len(result))
        else:
            value = result

        was_model = False

        if isinstance(value, Model):
            # by_alias is not supported yet by `odmantic.dict()`.
            model_or_value = value.dict()
            was_model = True
        else:
            model_or_value = value

        if was_model and current_app.config["QUART_MONGO_CONVERT_CASING"]:
            model_or_value = decamelize(model_or_value)

        return await func((model_or_value, status_or_headers, headers))

    return decorator
