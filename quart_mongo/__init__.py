"""
quart_mongo

Mongo DB extension for Quart.
"""
from .const import ASCENDING, DESCENDING
from .core import Mongo

__all__ = (
    "ASCENDING",
    "DESCENDING",
    "Mongo"
)
