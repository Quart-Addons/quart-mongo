"""
Test Odmantic Testing Class.
"""
from typing import Optional

import pytest
from odmantic import Model, Field
from quart import Quart

from quart_mongo import (
    DataSource,
    register_odmantic_schema,
    ResponseReturnValue, 
    mongo_validate_request)

from quart_mongo.typing import ODM_Model

class Details(Model):
    id: int = Field(primary_field=True)
    name: str
    age: Optional[int]

@pytest.mark.asyncio
async def test_send_json() -> None:
    """
    Test sending JSON
    """
    app = Quart(__name__)
    register_odmantic_schema(app)

    @app.route("/", methods=["POST"])
    @mongo_validate_request(Details)
    async def index(data: ODM_Model) -> ResponseReturnValue:
        return data

    client = app.test_client()
    response = await client.post("/", json=Details(id=1, name="bob", age=2))
    assert (await response.get_json()) == {"id": 1, "name": "bob", "age": 2}

@pytest.mark.asyncio
async def test_send_form() -> None:
    """
    Test sending from Form.
    """
    app = Quart(__name__)
    register_odmantic_schema(app)

    @app.route("/", methods=["POST"])
    @mongo_validate_request(Details, source=DataSource.FORM)
    async def index(data: Details) -> ResponseReturnValue:
        return data

    client = app.test_client()
    response = await client.post("/", form=Details(id=1, name="bob", age=2))
    assert (await response.get_json()) == {"id": 1, "name": "bob", "age": 2}


    