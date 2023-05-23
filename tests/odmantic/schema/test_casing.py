import pytest
from odmantic import Model, Field
from quart import Quart
from quart_schema import QuartSchema, validate_request, validate_response, ResponseReturnValue

class Data(Model):
    id: str = Field(primary_field=True)
    snake_case: str

@pytest.mark.asyncio
async def test_request_casing() -> None:
    app = Quart(__name__)
    QuartSchema(app, convert_casing=True)

    @app.route("/", methods=["POST"])
    @validate_request(Data)
    async def index(data: Data) -> ResponseReturnValue:
        return str(data.doc())

    client = app.test_client()
    response = await client.post("/", json={"id": "Hello", "snakeCase": "World"})
    assert await response.get_data(as_text=True) == "{'_id': 'Hello', 'snake_case': 'World'}"

@pytest.mark.asyncio
async def test_response_casing() -> None:
    app = Quart(__name__)
    QuartSchema(app, convert_casing=True)

    @app.route("/", methods=["GET"])
    @validate_response(Data)
    async def index() -> ResponseReturnValue:
        return Data(id="Hello", snake_case="World")

    client = app.test_client()
    response = await client.get("/")
    assert await response.get_data(as_text=True) == '{"id":"Hello","snakeCase":"World"}'
