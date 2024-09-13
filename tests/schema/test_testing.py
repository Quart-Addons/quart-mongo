"""
Tests the testing class for quart_schema.
"""
import pytest
from quart import Quart

from quart_schema import (
    DataSource,
    QuartSchema,
    validate_request
    )

from quart_mongo import Mongo

from tests.odmantic.models import Things


@pytest.mark.asyncio
async def test_send_json(uri: str) -> None:
    """
    Tests sending JSON.
    """
    app = Quart(__name__)
    QuartSchema(app)
    Mongo(app, uri)

    @app.route("/", methods=["POST"])
    @validate_request(Things)
    async def index(data: Things) -> Things:
        return data

    client = app.test_client()
    response = await client.post("/", json=Things(id="Hello", val="World"))
    assert (await response.get_json()) == {"id": "Hello", "val": "World"}


@pytest.mark.asyncio
async def test_send_form(uri: str) -> None:
    """
    Tests sending form data.
    """
    app = Quart(__name__)
    QuartSchema(app)
    Mongo(app, uri)

    @app.route("/", methods=["POST"])
    @validate_request(Things, source=DataSource.FORM)
    async def index(data: Things) -> Things:
        return data

    client = app.test_client()
    response = await client.post("/", form=Things(id="Hello", val="World"))
    assert (await response.get_json()) == {"id": "Hello", "val": "World"}
