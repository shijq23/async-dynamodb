import pytest
from httpx import AsyncClient, ASGITransport
from moto import mock_aws
import os

import pytest_asyncio

# Set dummy AWS credentials for moto
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest_asyncio.fixture(scope="function")
async def aws_credentials():
    with mock_aws():
        yield


@pytest.mark.asyncio
async def test_create_item(aws_credentials):
    """
    Test the /items/{item_id} endpoint.
    """
    from my_app.main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/items/test-item-1")
        assert response.status_code == 200
        assert response.json() == {"status": "success", "item_id": "test-item-1"}