import pytest
from odmantic import Model
from quart import Quart
from quart_schema import DataSource, QuartSchema, ResponseReturnValue, validate_request

@pytest.mark.asyncio
async def test_send_json() -> None:
    app = Quart(__name__)
    QuartSchema(app)
    