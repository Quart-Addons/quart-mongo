"""
tests.odmantic.quart_schema.test_testing
"""
import pytest

from quart import Quart
from quart.typing import TestClientProtocol

from quart_schema import (
    DataSource,
    validate_request
)

from tests.odmantic.models import Things


@pytest.fixture
async def test_client(app: Quart) -> TestClientProtocol:
    """
    Test client
    """
    @app.post("/json")
    @validate_request(Things)
    async def json(data: Things) -> Things:
        """
        test route
        """
        return data

    @app.post("/form")
    @validate_request(Things, source=DataSource.FORM)
    async def form(data: Things) -> Things:
        """
        test route that returns a model
        when form as the data source
        """
        return data

    return app.test_client()


@pytest.mark.asyncio
async def test_send_json(test_client: TestClientProtocol) -> None:
    """
    Tests sending JSON.
    """
    things = Things(id="Hello", val="World")
    response = await test_client.post("/json", json=things)
    assert (await response.get_json()) == {"id": "Hello", "val": "World"}


@pytest.mark.asyncio
async def test_send_form(test_client: TestClientProtocol) -> None:
    """
    Tests sending form data.
    """
    things = Things(id="Hello", val="World")
    response = await test_client.post("/form", form=things)
    assert (await response.get_json()) == {"id": "Hello", "val": "World"}
