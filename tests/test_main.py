import pytest
from httpx import AsyncClient, ASGITransport
from moto import mock_aws
import os

from my_app.main import app

# Set dummy AWS credentials for moto
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.mark.asyncio
async def test_create_item():
    """
    Test the /items/{item_id} endpoint.
    The @mock_aws decorator intercepts boto3 calls.
    """
    # Use moto as a context manager so the async test function remains async
    with mock_aws():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # The lifespan event will create the table in the mocked environment
            await app.router.startup()

            response = await client.post("/items/test-item-1")
            assert response.status_code == 200
            assert response.json() == {"status": "success", "item_id": "test-item-1"}
