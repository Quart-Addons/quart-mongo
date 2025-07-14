"""
tests.test_url_converter
"""
import pytest

from bson import ObjectId
from werkzeug.exceptions import NotFound
from werkzeug.routing.map import Map

from quart_mongo import BSONObjectIdConverter


def test_bson_object_id_converter() -> None:
    """
    Test the ObjectId url converter
    """
    converter = BSONObjectIdConverter(Map())

    with pytest.raises(NotFound):
        converter.to_python("123")

    assert converter.to_python("4e4ac5cfffc84958fa1f45fb") == ObjectId(
        "4e4ac5cfffc84958fa1f45fb"
    )
    assert converter.to_url(ObjectId("4e4ac5cfffc84958fa1f45fb")) == \
        "4e4ac5cfffc84958fa1f45fb"
