"""
quart_mongo.typing
"""
from __future__ import annotations

from typing import Any, AnyStr, Dict, Optional, Tuple, Type, TYPE_CHECKING, TypeVar, Union

from odmantic import Model as OdmModel
from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic.dataclasses import Dataclass

Model = Union[Type[OdmModel], Type[BaseModel], Type["Dataclass"], Type]
PydanticModel = Union[Type[OdmModel], Type[BaseModel], Type["Dataclass"]]