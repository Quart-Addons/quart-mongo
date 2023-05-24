"""
quart_mongo.typing
"""
from __future__ import annotations

from bson.codec_options import CodecOptions as _CodecOptions
from bson.json_util import JSONOptions as _JSONOptions
import motor.core
from pymongo.read_preferences import _ServerMode
from pymongo.read_concern import ReadConcern as _ReadConcern
from pymongo.write_concern import WriteConcern as _WriteConcern

AgnosticBaseProperties = motor.core.AgnosticBaseProperties

CodecOptions = _CodecOptions

ReadConcern = _ReadConcern

ServerMode = _ServerMode

WriteConcern = _WriteConcern

JSONOptions = _JSONOptions
