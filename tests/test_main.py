import pytest
from httpx import AsyncClient, ASGITransport
from moto import mock_aws
import os

from my_app.main import app
from my_app.dynamodb import settings
import pytest_asyncio

# Set dummy AWS credentials for moto
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_REGION"] = "us-east-1" # Also mock the region

@pytest_asyncio.fixture(scope="function")
async def aws_credentials():
    with mock_aws():
        settings.dynamodb_endpoint_url = None
        yield

@pytest.mark.asyncio
async def test_create_item(aws_credentials):
    """
    Test the /items/{item_id} endpoint with mocked DynamoDB.
    The @mock_aws decorator intercepts all aioboto3 calls.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # The lifespan event will create the table in the mocked environment
        # because @mock_aws is active.
        await app.router.startup()

        response = await client.post("/items/test-item-1")
        assert response.status_code == 200
        assert response.json() == {"status": "success", "item_id": "test-item-1"}

        # The lifespan shutdown will also be mocked.
        await app.router.shutdown()