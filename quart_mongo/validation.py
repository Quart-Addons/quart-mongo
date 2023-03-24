"""
quart_mongo.validation
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import auto, Enum
from functools import wraps
from typing import Any, Callable, cast, Dict, Optional, Tuple, Type, TypeVar, Union

from humps import decamelize
from odmantic import Model as OdmModel
from pydantic import BaseModel, ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic.schema import model_schema
from .typing import Model, PydanticModel


class DataSource(Enum):
    """
    Request type data source.
    """
    FORM = auto()
    JSON = auto()

def validate_request(
        model_class,
        *,
        source: DataSource = DataSource.JSON
) -> Callable:
    """
    Validate the request.
    """
    pass

def _to_pydantic_model(model_class: Model) -> PydanticModel:
    """
    Converts a model class to a pydantic or odmantic model.
    """
    pydantic_model_class: PydanticModel
    if is_dataclass(model_class):
        pydantic_model_class = pydantic_dataclass(model_class) # type: ignore
    else:
        pydantic_model_class = cast(PydanticModel, model_class)
    return pydantic_model_class
