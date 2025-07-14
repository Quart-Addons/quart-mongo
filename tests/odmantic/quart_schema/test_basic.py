"""
tests.odmantic.quart_schema.test_basic
"""
from pathlib import Path
from uuid import UUID

import pytest
from bson import ObjectId
from odmantic import Model
from quart import Quart
from quart.typing import TestClientProtocol

from tests.odmantic.models import Things


class OdmanticEncoded(Model):
    """
    Model for testing.
    """
    a: UUID
    b: Path


@pytest.fixture
async def test_client(app: Quart) -> TestClientProtocol:
    """
    Test client
    """
    @app.get("/")
    async def index() -> Things:
        """
        test route
        """
        return Things(id="foo", val="bar")

    @app.get("/encode")
    async def encoded() -> OdmanticEncoded:
        """
        test route that returns a model
        with encoding
        """
        oid = ObjectId("5cf29abb5167a14c9e6e12c4")
        return OdmanticEncoded(
            a=UUID("23ef2e02-1c20-49de-b05e-e9fe2431c474"), b=Path("/")
            )

    return app.test_client()


@pytest.mark.asyncio
async def test_make_response(test_client: TestClientProtocol) -> None:
    """
    Test make response with quart_schema.
    """
    response = await test_client.get("/")
    assert (await response.get_json()) == {"id": "foo", "val": "bar"}


@pytest.mark.asyncio
async def test_make_odmantic_encoder_response(
    test_client: TestClientProtocol
) -> None:
    """
    Tests encoder response with quart_schema.
    """
    response = await test_client.get("/encode")
    
    assert (await response.get_json()) == {"a": "23ef2e02-1c20-49de-b05e-e9fe2431c474", "b": "/"}
