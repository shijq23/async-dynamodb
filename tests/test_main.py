from typing import Any, Generator
from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
import pytest
from httpx import AsyncClient, ASGITransport
from moto.server import ThreadedMotoServer
from unittest.mock import AsyncMock

from my_app.main import app, create_item
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
@pytest.mark.integration
async def test_create_item_async(client: AsyncClient):
    """
    Test the /items/{item_id} endpoint with mocked DynamoDB.
    """
    response = await client.post("/items/test-item-1")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "item_id": "test-item-1"}

@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_item_sync(test_client: TestClient):
    """
    Test the /items/{item_id} endpoint with mocked DynamoDB.
    """
    response = test_client.post("/items/test-item-1")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "item_id": "test-item-1"}

@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_item_unit():
    """
    Test the create_item handler in isolation with a mocked DynamoDB resource.
    """
    # 1. Create a mock for the DynamoDB resource dependency
    mock_dynamodb = AsyncMock()
    mock_table = AsyncMock()

    # Configure the mock resource to return a mock table object
    mock_dynamodb.Table.return_value = mock_table

    # 2. Call the handler function directly with the mock
    item_id = "unit-test-item"
    response = await create_item(item_id=item_id, dynamodb=mock_dynamodb)

    # 3. Assert that the mocked methods were called correctly
    mock_dynamodb.Table.assert_called_once_with("items")
    mock_table.put_item.assert_awaited_once_with(Item={"id": item_id, "name": f"Item {item_id}"})
    assert response == {"status": "success", "item_id": item_id}