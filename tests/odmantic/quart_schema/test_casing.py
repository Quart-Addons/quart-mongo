"""
tests.odmantic.quart_schema.test_casing
"""
import pytest

from odmantic import Model, Field
from quart import Quart
from quart.typing import TestClientProtocol

from quart_schema import (
    validate_request,
    validate_response,
    ResponseReturnValue
)


class Data(Model):
    """
    Test data model.
    """
    id: str = Field(primary_field=True)
    snake_case: str


@pytest.fixture
async def test_client(app: Quart) -> TestClientProtocol:
    """
    Test client
    """
    app.config["QUART_SCHEMA_CONVERT_CASING"] = True

    @app.post("/")
    @validate_request(Data)
    async def post(data: Data) -> ResponseReturnValue:
        """
        test request
        """
        return str(data.model_dump_doc())

    @app.get("/")
    @validate_response(Data)
    async def get() -> Data:
        """
        test route that returns a model
        when form as the data source
        """
        return Data(id="Hello", snake_case="World")

    return app.test_client()


@pytest.mark.asyncio
async def test_request_casing(test_client: TestClientProtocol) -> None:
    """
    Test camel casing with request.
    """
    response = await test_client.post(
        "/", json={"id": "Hello", "snakeCase": "World"}
        )
    assert await response.get_data(as_text=True) == \
        "{'_id': 'Hello', 'snake_case': 'World'}"


@pytest.mark.asyncio
async def test_response_casing(test_client: TestClientProtocol) -> None:
    """
    Test camel casing with response.
    """
    response = await test_client.get("/")
    assert await response.get_data(as_text=True) == \
        '{"id":"Hello","snakeCase":"World"}\n'
