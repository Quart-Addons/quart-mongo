"""
tests.odmantic.quart_schema.test_validation
"""
from typing import Any

import pytest
from odmantic import Model
from quart import Quart, websocket
from quart.views import View

from quart_schema import (
    DataSource,
    ResponseReturnValue,
    SchemaValidationError,
    validate_request,
    validate_response
)

from tests.odmantic.models import Things


# pylint: disable=W0613


class Invalid(Model):
    """
    Invalid Model
    """
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
async def test_request_validation(app: Quart, json: dict, status: int) -> None:
    """
    Tests request validation.
    """
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
    app: Quart, data: dict, status: int
) -> None:
    """
    Tests request form validation.
    """
    @app.post("/")
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
    app: Quart, return_value: Any, status: int
) -> None:
    """
    Tests response validation.
    """
    @app.get("/")
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
    app: Quart, return_value: Any, status: int
) -> None:
    """
    Tests view response validation.
    """
    class ValidatedView(View):
        """
        Test validated view
        """
        decorators = [validate_response(Things)]
        methods = ["GET"]

        async def dispatch_request(self, **kwargs: Any) -> ResponseReturnValue:
            """
            dispatch request
            """
            return return_value

    app.add_url_rule("/", view_func=ValidatedView.as_view("view"))

    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == status


@pytest.mark.asyncio
async def test_websocket_validation(app: Quart) -> None:
    """
    Test websocket validation.
    """
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
