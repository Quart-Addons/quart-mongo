"""
Test casing.
"""
import pytest

from odmantic import Model, Field
from quart import Quart

from quart_mongo import (
    register_odmantic_schema,
    ResponseReturnValue,
    mongo_validate_request,
    mongo_validate_response
)

class Data(Model):
    snake_case: str

@pytest.mark.asyncio
async def test_request_casing() -> None:
    """
    Test request casing.
    """
    app = Quart(__name__)
    register_odmantic_schema(app, convert_casing=True)

    @app.route("/", methods=["POST"])
    @mongo_validate_request(Data)
    async def index(data: Data) -> ResponseReturnValue:
        return str(data.dict())
    
    client = app.test_client()
    response = await client.post("/", json={"snakeCase": "Hello"})
    assert await response.get_data(as_text=True) == "{'snake_case': 'Hello'}"