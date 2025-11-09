import pytest
from httpx import AsyncClient, ASGITransport
from moto.server import ThreadedMotoServer
import os

from my_app.main import app
from my_app.dynamodb import settings
import pytest_asyncio
import requests

# Set dummy AWS credentials for moto
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_REGION"] = "us-east-1" # Also mock the region

@pytest.fixture(scope="module")
def aws_credentials():
    """
    Fixture to run a moto server for mocking AWS services.
    The server is started once per module and torn down after all tests in the module have run.
    """
    server = ThreadedMotoServer(port=5000)
    server.start()
    host, port = server.get_host_and_port()
    endpoint_url = f"http://127.0.0.1:{port}"
    
    # Configure the application to use the moto server endpoint
    settings.dynamodb_endpoint_url = endpoint_url
    yield endpoint_url
    
    server.stop()

@pytest.mark.asyncio
async def test_create_item(aws_credentials):
    """
    Test the /items/{item_id} endpoint with mocked DynamoDB.
    The @mock_aws decorator intercepts all aioboto3 calls.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # The lifespan event will create the table in the mocked environment
        # by connecting to the moto server.
        response = await client.post("/items/test-item-1")
        assert response.status_code == 200
        assert response.json() == {"status": "success", "item_id": "test-item-1"}