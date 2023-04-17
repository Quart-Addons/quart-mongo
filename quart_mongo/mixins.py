"""
quart_mongo.odm_models.mixins
"""
from typing import Any, AnyStr, cast, Dict, Optional, Tuple, Type, Union

from humps import camelize, decamelize
from odmantic import Model
from pydantic import ValidationError
from quart import current_app, Response
from quart.datastructures import FileStorage
from quart.testing.utils import sentinel
from werkzeug.datastructures import Authorization, Headers

from .typing import ODM, TestClientProtocol, WebsocketProtocol

class SchemaValidationError(Exception):
    """
    Schema Validation Error.
    """
    def __init__(self, validation_error: Optional[ValidationError] = None) -> None:
        super().__init__()
        self.validation_error = validation_error

class WebsocketMixin:
    """
    Websocket Mixin Class for `Odmantic` Models.
    """
    async def reieve_as_odm(
            self: WebsocketProtocol, model_class: ODM
    ) -> ODM:
        """
        Recieve websocket data as an `Odmantic` model.

        Arguments:
            model_class: The `Odmantic` model to be used
                for the recieved data.
        """
        data = await self.receive_json()

        if current_app.config["QUART_MONGO_CONVERT_CASING"]:
            data = decamelize(data)

        try:
            return model_class(**data)
        except ValidationError as error:
            raise SchemaValidationError(error)

    async def send_as_odm(
            self: WebsocketProtocol, value: Any, model_class: Type[ODM]
    ) -> None:
        """
        Send an `Odmantic` Model via Websocket.

        Arguments:
            value: The data to send. 
            model_class: The `Odmantic` model to use.
        """
        if isinstance(value, dict):
            try:
                model_value = model_class(**value)
            except ValidationError as error:
                raise SchemaValidationError(error)
        elif isinstance(value, model_class):
            model_value = value
        else:
            raise SchemaValidationError()

        model_value = cast(ODM, model_value)
        data = model_value.dict()

        if current_app.config["QUART_MONGO_CONVERT_CASING"]:
            data = camelize(data)

        await self.send_json(data)

class TestClientMixin:
    """
    Test Client Mixin Class for Odmantic Models.
    """
    async def _make_request(
            self: TestClientProtocol,
            path: str,
            method: str,
            headers: Optional[Union[dict, Headers]],
            data: Optional[AnyStr],
            form: Optional[dict],
            files: Optional[Dict[str, FileStorage]],
            query_string: Optional[dict],
            json: Any,
            scheme: str,
            root_path: str,
            http_version: str,
            scope_base: Optional[dict],
            auth: Optional[Union[Authorization, Tuple[str, str]]] = None,
            subdomain: Optional[str] = None,
    ) -> Response:
        if json is not sentinel:
            was_model = False

            if isinstance(json, Model):
                json = json.dict()
                was_model = True

            if was_model and self.app.config["QUART_MONGO_CONVERT_CASING"]:
                json = camelize(json)

        if form is not None:
            was_model = False

            if isinstance(form, Model):
                form = form.dict()
                was_model = True

            if was_model and self.app.config["QUART_MONGO_CONVERT_CASING"]:
                form = camelize(form)

        if query_string is not None:
            was_model = False

            if isinstance(query_string, Model):
                query_string = query_string.dict()
                was_model = True

            if was_model and self.app.config["QUART_MONGO_CONVERT_CASING"]:
                query_string = camelize(query_string)

        return await super()._make_request(
            path,
            method,
            headers,
            data,
            form,
            files,
            query_string,
            json,
            scheme,
            root_path,
            json,
            scheme,
            root_path,
            http_version,
            scope_base,
            auth,
            subdomain
        )
