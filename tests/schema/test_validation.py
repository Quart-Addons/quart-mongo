"""
Tests validation with quart_schema.
"""
from typing import Any

import pytest
from odmantic import Model
from quart import Quart, websocket
from quart.views import View

from quart_schema import (
    DataSource,
    QuartSchema,
    ResponseReturnValue,
    SchemaValidationError,
    validate_request,
    validate_response
)

from quart_mongo import Mongo

from tests.odmantic.models import Things


class Invalid(Model):
    name: str


VALID_DICT = {"id": "Hello", "val": "World"}
INVALID_DICT = {"name": "bob"}
VALID = Things(id="Hello", val="World")
INVALID = Invalid(name="bob")


@pytest.mark.parametrize(
    "json, status",
    [
        (VALID_DICT, 200),
        (INVALID_DICT, 400),
    ],
)
@pytest.mark.asyncio
async def test_request_validation(uri: str, json: dict, status: int) -> None:
    """
    Tests request validation.
    """
    app = Quart(__name__)
    QuartSchema(app)
    Mongo(app, uri)

    @app.route("/", methods=["POST"])
    @validate_request(Things)
    async def index(data: Things) -> ResponseReturnValue:
        return ""

    client = app.test_client()
    response = await client.post("/", json=json)
    assert response.status_code == status


@pytest.mark.parametrize(
    "data, status",
    [
        ({"id": "hello", "val": "world"}, 200),
        ({"age": 2}, 400),
    ],
)
@pytest.mark.asyncio
async def test_request_form_validation(
    uri: str, data: dict, status: int
) -> None:
    """
    Tests request form validation.
    """
    app = Quart(__name__)
    QuartSchema(app)
    Mongo(app, uri)

    @app.route("/", methods=["POST"])
    @validate_request(Things, source=DataSource.FORM)
    async def index(data: Things) -> ResponseReturnValue:
        return ""

    client = app.test_client()
    response = await client.post("/", form=data)
    assert response.status_code == status


@pytest.mark.parametrize(
        "return_value, status",
        [
            (VALID_DICT, 200),
            (INVALID_DICT, 500),
            (VALID, 200),
            (INVALID, 500)
        ],
)
@pytest.mark.asyncio
async def test_response_validation(
    uri: str, return_value: Any, status: int
) -> None:
    """
    Tests response validation.
    """
    app = Quart(__name__)
    QuartSchema(app)
    Mongo(app, uri)

    @app.route("/")
    @validate_response(Things)
    async def index() -> ResponseReturnValue:
        return return_value

    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == status


@pytest.mark.parametrize(
    "return_value, status",
    [
        (VALID_DICT, 200),
        (INVALID_DICT, 500),
    ],
)
@pytest.mark.asyncio
async def test_view_response_validation(
    uri: str, return_value: Any, status: int
) -> None:
    """
    Tests view response validation.
    """
    class ValidatedView(View):
        decorators = [validate_response(Things)]
        methods = ["GET"]

        def dispatch_request(self, **kwargs: Any) -> ResponseReturnValue:
            return return_value

    app = Quart(__name__)
    QuartSchema(app)
    Mongo(app, uri)

    app.add_url_rule("/", view_func=ValidatedView.as_view("view"))

    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == status


@pytest.mark.asyncio
async def test_websocket_validation(uri: str) -> None:
    """
    Test websocket validation.
    """
    app = Quart(__name__)
    QuartSchema(app)
    Mongo(app, uri)

    @app.websocket("/ws")
    async def ws() -> None:
        await websocket.receive_as(Things)
        with pytest.raises(SchemaValidationError):
            await websocket.receive_as(Things)
        await websocket.send_as(VALID_DICT, Things)
        with pytest.raises(SchemaValidationError):
            await websocket.send_as(VALID_DICT, Invalid)

    client = app.test_client()
    async with client.websocket("/ws") as test_websocket:
        await test_websocket.send_json(VALID_DICT)
        await test_websocket.send_json(INVALID_DICT)
