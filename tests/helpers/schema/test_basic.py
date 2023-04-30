"""
Test basic schema.
"""
import pytest

from quart import Quart
from quart_mongo import register_mongo_helpers, ResponseReturnValue

from tests.odmantic.models import Things

@pytest.mark.asyncio
async def test_make_response() -> None:
    """
    Test make response.
    """
    app = Quart(__name__)
    register_mongo_helpers(app)

    @app.route("/")
    async def index() -> ResponseReturnValue:
        return Things(id="foo", val="bar")

    client = app.test_client()
    response = await client.get("/")
    assert (await response.get_json()) == {"id": "foo", "val": "bar"}
