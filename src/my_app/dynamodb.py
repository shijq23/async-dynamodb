import aioboto3
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_region: str = "us-east-1"
    dynamodb_endpoint_url: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()


def get_session():
    """Get or create aioboto3 session with current settings"""
    return aioboto3.Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
        
    )


@asynccontextmanager
async def dynamodb_resource_manager():
    """Dependency to get a DynamoDB resource.
    Context manager to get a DynamoDB resource.
    This is the context maanager.
    """
    session = get_session()
    async with session.resource("dynamodb", endpoint_url=settings.dynamodb_endpoint_url) as resource:
        yield resource


async def get_dynamodb():
    """Dependency to get a DynamoDB resource for endpoints.
    This is the actual dynamodb resource provider.
    """
    async with dynamodb_resource_manager() as resource:
        yield resource
