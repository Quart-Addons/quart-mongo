"""
Test Register Helpers.
"""
from quart import Quart
from quart_mongo import Mongo, register_mongo_helpers, MongoJSONProvider

def test_register_mongo_helpers() -> None:
    """
    Test the register mongo helpers function.
    """
    app = Quart(__name__)
    register_mongo_helpers(app)

    assert app.config["QUART_MONGO_BSON_CONVERTER"] is True
    assert app.config["QUART_MONGO_JSON_PROVIDER"] is True
    assert app.config["QUART_MONGO_JSON_OPTIONS"] is None
    assert app.config["QUART_MONGO_SCHEMA"] is True
    assert app.config["QUART_MONGO_CONVERT_CASING"] is False

    assert "ObjectId" in app.url_map.converters
    assert isinstance(app.json, MongoJSONProvider)

def test_register_mongo_helpers_shortcut(client_uri: str) -> None:
    """
    Test the register mongo helpers function.
    """
    app = Quart(__name__)
    mongo = Mongo(app, client_uri)
    
    mongo.register_helpers(
        app,
        False,
        False,
        None,
        False,
        True
    )

    assert app.config["QUART_MONGO_BSON_CONVERTER"] is False
    assert app.config["QUART_MONGO_JSON_PROVIDER"] is False
    assert app.config["QUART_MONGO_JSON_OPTIONS"] is None
    assert app.config["QUART_MONGO_SCHEMA"] is False
    assert app.config["QUART_MONGO_CONVERT_CASING"] is True
