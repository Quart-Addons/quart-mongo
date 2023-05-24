"""
Test BSON URL Converter.
"""
import pytest

from bson import ObjectId
from werkzeug.exceptions import NotFound
from quart_mongo.helpers import BSONObjectIdConverter

def test_bson_url_converter() -> None:
    """
    Test BSON URL Converter.
    """
    converter = BSONObjectIdConverter("/")

    with pytest.raises(NotFound):
        converter.to_python("123")

    assert converter.to_python("4e4ac5cfffc84958fa1f45fb") == \
        ObjectId("4e4ac5cfffc84958fa1f45fb")

    assert converter.to_url(ObjectId("4e4ac5cfffc84958fa1f45fb")) == \
        "4e4ac5cfffc84958fa1f45fb"
