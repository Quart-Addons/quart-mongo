"""
quart_mongo.odm_models.mixins
"""
from typing import Any, AnyStr, cast, Dict, Optional, overload, Tuple, Type, Union

from humps import camelize, decamelize
from pydantic import ValidationError
from quart import current_app, Response

from .typing import ODM, TestClientProtocol, WebsocketProtocol

class SchemaValidationError(Exception):
    def __init__(self, validation_error: Optional[ValidationError] = None) -> None:
        super().__init__()
        self.validation_error = validation_error

class WebsocketMixin:
    @overload
    async def recieve_as(self: WebsocketProtocol, model_class: Type[ODM]) -> ODM:
        ...

    async def reieve_as(
            self: WebsocketProtocol, model_class: ODM
    ) -> ODM:

        data = await self.receive_json()

        if current_app.config["MONGO_CONVERT_CASING"]:
            data = decamelize(data)

        try:
            return model_class(**data)
        except ValidationError as error:
            raise SchemaValidationError(error)

    async def send_as(
            self: WebsocketProtocol, value: Any, model_class: Type[ODM]
    ) -> None:
        if isinstance(value, dict):
            try:
                model_value = model_class(**value)
            except ValidationError as error:
                raise SchemaValidationError(error)
        elif isinstance(value, model_class):
            model_value = value
        else:
            raise SchemaValidationError()

        data = model_value.dict()

        if current_app.config["MONGO_CONVERT_CASING"]:
            data = camelize(data)

        await self.send_json(data)
