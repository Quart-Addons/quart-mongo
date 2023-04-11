"""
quart_mongo.typing
"""
from __future__ import annotations
import typing as t

from odmantic import Model as ODM_Model
from pydantic import BaseModel

if t.TYPE_CHECKING:
    from pydantic.dataclasses import Dataclass

Model = t.Union[t.Type[ODM_Model], t.Type[BaseModel], t.Type["Dataclass"], t.Type]

BM = t.TypeVar("BM", bound=BaseModel)
DC = t.TypeVar("DC", bound="Dataclass")
