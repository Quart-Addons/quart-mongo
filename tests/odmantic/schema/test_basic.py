"""
Test basic schema.
"""
import pytest

from quart import Quart
from quart_mongo import register_odmantic_schema, ResponseReturnValue
from quart_mongo.typing import ODM_Model

from ..models import Things

@pytest.mark.asyncio
async def test_make_response() -> None:
    """
    Test make response.
    """
    app = Quart(__name__)
    register_odmantic_schema(app)

    @app.route("/")
    async def index() -> ResponseReturnValue:
        return Things(id="foo", val="bar")

    client = app.test_client()
    response = await client.get("/")
    assert (await response.get_json()) == {"id": "foo", "val": "bar"}
