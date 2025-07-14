"""
quart_mongo.motor.typing
"""
from __future__ import annotations

import motor.core
from bson.codec_options import CodecOptions as _CodecOptions
from pymongo.read_preferences import _ServerMode
from pymongo.read_concern import ReadConcern as _ReadConcern
from pymongo.write_concern import WriteConcern as _WriteConcern


AgnosticBaseProperties = motor.core.AgnosticBaseProperties

CodecOptions = _CodecOptions

ReadConcern = _ReadConcern

ServerMode = _ServerMode

WriteConcern = _WriteConcern
