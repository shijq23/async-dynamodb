from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from my_app.dynamodb import dynamodb_resource_manager, get_dynamodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup, create a table for demonstration
    print("Creating DynamoDB table 'items'...")
    async with dynamodb_resource_manager() as dynamodb:
        try:
            await dynamodb.create_table(
                TableName="items",
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            )
            print("Table 'items' created.")
        except Exception as e:
            # Handle case where table already exists
            print(f"Could not create table, it might already exist. Error: {e}")
        table = await dynamodb.Table("items")
        await table.wait_until_exists()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Welcome to the aioboto3 FastAPI app!"}


@app.post("/items/{item_id}")
async def create_item(item_id: str, dynamodb=Depends(get_dynamodb)):
    """Creates an item in the DynamoDB table."""
    table = await dynamodb.Table("items")
    await table.put_item(Item={"id": item_id, "name": f"Item {item_id}"})
    return {"status": "success", "item_id": item_id}
