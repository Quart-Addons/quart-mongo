"""
quart_mongo.typing
"""
from __future__ import annotations
import typing as t

from odmantic import Model as ODM_Model
from pydantic import BaseModel
from quart import Quart
from quart.datastructures import FileStorage
from quart.typing import (
    HeadersValue as QuartHeadersValue,
    ResponseReturnValue as QuartResponseReturnValue,
    ResponseValue as QuartResponseValue,
    StatusCode,
)
from quart.wrappers import Response
from werkzeug.datastructures import Headers

if t.TYPE_CHECKING:
    from pydantic.dataclasses import Dataclass

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol # type: ignore

Model = t.Union[t.Type[ODM_Model], t.Type[BaseModel], t.Type["Dataclass"], t.Type]
PydanticModel = t.Union[t.Type[BaseModel], t.Type["Dataclass"]]

ResponseValue = t.Union[QuartResponseValue, ODM_Model]
HeadersValue = t.Union[QuartHeadersValue, PydanticModel]

ResponseReturnValue = t.Union[
    QuartResponseReturnValue,
    ResponseValue,
    t.Tuple[ResponseValue, HeadersValue],
    t.Tuple[ResponseValue, StatusCode],
    t.Tuple[ResponseValue, StatusCode, HeadersValue]
]

class WebsocketProtocol(Protocol):
    async def receive_json(self) -> dict:
        ...

    async def send_json(self, data: dict) -> None:
        ...


class TestClientProtocol(Protocol):
    app: Quart

    async def _make_request(
        self,
        path: str,
        method: str,
        headers: t.Optional[t.Union[dict, Headers]],
        data: t.Optional[t.AnyStr],
        form: t.Optional[dict],
        files: t.Optional[t.Dict[str, FileStorage]],
        query_string: t.Optional[dict],
        json: t.Any,
        scheme: str,
        root_path: str,
        http_version: str,
        scope_base: t.Optional[dict],
    ) -> Response:
        ...

BM = t.TypeVar("BM", bound=BaseModel)
DC = t.TypeVar("DC", bound="Dataclass")
