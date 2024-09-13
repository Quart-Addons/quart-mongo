"""
quart_mongo.const
"""
import pymongo

DESCENDING = pymongo.DESCENDING
"""Descending sort order."""

ASCENDING = pymongo.ASCENDING
"""Ascending sort order."""

DB_NAME_ERROR = "The database name needs to be set in the Mongo URI or \
    passed to Odmantic class directly."

MONGO_URI_ERROR = "You must specify a URI or set the MONGO_URI Quart config \
    variable."

GRIDFS_CACHE = "'cache_for' must be an integer."
GRIDFS_FILEOBJ = "'fileobj' must have read() method."
GRIDFS_STRING = "'base' must be a string or unicode."
GRIDFS_VERSION = "'version' must be an integer."

ODMANTIC_MODEL = "The model must a subclass of an Odmantic model."
ODMANTIC_MODEL_APP = "There are no Odmantic Models registered with the \
    application."
ODMANTIC_MODELS = "One or more of the models provided are not a subclass of \
    an Odmantic model."
