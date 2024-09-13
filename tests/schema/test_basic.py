"""
tests.schema.test_basic
"""
from pathlib import Path
from uuid import UUID

import pytest
from bson import ObjectId
from odmantic import Model
from quart import Quart
from quart_schema import QuartSchema
from quart_mongo import Mongo

from tests.odmantic.models import Things


@pytest.mark.asyncio
async def test_make_response(uri: str) -> None:
    """
    Test make response with quart_schema.
    """
    app = Quart(__name__)
    QuartSchema(app)
    Mongo(app, uri)

    @app.route("/")
    async def index() -> Things:
        return Things(id="foo", val="bar")

    client = app.test_client()
    response = await client.get("/")
    assert (await response.get_json()) == {"id": "foo", "val": "bar"}


class OdmanticEncoded(Model):
    """
    Model for testing.
    """
    a: UUID
    b: Path


@pytest.mark.asyncio
async def test_make_odmantic_encoder_response(uri: str) -> None:
    """
    Tests encoder response with quart_schema.
    """
    app = Quart(__name__)
    app.config.setdefault("QUART_MONGO_JSON_OPTIONS", None)
    QuartSchema(app)
    Mongo(app, uri)

    id = ObjectId("5cf29abb5167a14c9e6e12c4")

    @app.route("/")
    async def index() -> OdmanticEncoded:
        return OdmanticEncoded(
            a=UUID("23ef2e02-1c20-49de-b05e-e9fe2431c474"), b=Path("/"), id=id
            )

    client = app.test_client()
    response = await client.get("/")
    assert (await response.get_json()) == \
        {
            "a": "23ef2e02-1c20-49de-b05e-e9fe2431c474",
            "b": "/",
            "id": {"$oid": "5cf29abb5167a14c9e6e12c4"}
            }
