from typing import Any, Generator
from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from moto import mock_aws
import pytest
from httpx import AsyncClient, ASGITransport
from moto.server import ThreadedMotoServer

from my_app.main import app
from my_app.dynamodb import settings
import requests
import os
import pytest_asyncio

# Set dummy AWS credentials for moto
# These must be set before any boto3/aioboto3 sessions are created.
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_REGION"] = "us-east-1"  # Mock a default region

@pytest.fixture(scope="session")
def aws_service():
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
    print(f"Using moto server at {endpoint_url} for DynamoDB endpoint.")
    yield endpoint_url
    
    server.stop()

@pytest.fixture(name="test_client", scope="function")
def test_client(aws_service) -> Generator[TestClient, Any, Any]:
    """Create a TestClient for the FastAPI app with dependency overrides cleared after each test."""
    with TestClient(app, raise_server_exceptions=False) as _client:
        yield _client
        app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(aws_service):
    """
    Fixture to create a httpx.AsyncClient that handles the lifespan of the app.
    This ensures that startup and shutdown events are run for each test function.
    """
    async with LifespanManager(app) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    """
    Test the /items/{item_id} endpoint with mocked DynamoDB.
    """
    response = await client.post("/items/test-item-1")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "item_id": "test-item-1"}

@pytest.mark.asyncio
async def test_create_item_sync(test_client: TestClient):
    """
    Test the /items/{item_id} endpoint with mocked DynamoDB.
    """
    response = test_client.post("/items/test-item-1")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "item_id": "test-item-1"}