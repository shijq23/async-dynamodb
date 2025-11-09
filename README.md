# FastAPI with aioboto3 and DynamoDB

This project is a sample FastAPI application that demonstrates asynchronous operations with AWS DynamoDB using the `aioboto3` library. The project is structured with source code in `src`, tests in `tests`, and uses `uv` for fast dependency management.

## Project Structure

```
/async-dynamodb
├── .env
├── pyproject.toml
├── README.md
├── src
│   └── my_app
│       ├── __init__.py
│       ├── dynamodb.py
│       └── main.py
└── tests
    └── test_main.py
```

-   **`src/`**: Contains the main application source code.
-   **`tests/`**: Contains the unit tests for the application.
-   **`pyproject.toml`**: Defines project metadata and dependencies.
-   **`.env`**: Stores environment variables for local development.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   Python (version 3.8 or higher)
-   uv: An extremely fast Python package installer and resolver.
-   Docker: Required for running a local DynamoDB instance for development.

## Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Clone the Repository

First, clone this repository to your local machine (or create the files as described).

```bash
git clone https://github.com/shijq23/async-dynamodb.git
cd async-dynamodb
```

### 2. Create a Virtual Environment

Using `uv`, create a virtual environment. This isolates the project's dependencies from your global Python installation.

```bash
uv venv
```

### 3. Activate the Virtual Environment

Activate the newly created environment. Your shell prompt should change to indicate that you are now in the `.venv` environment.

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows (PowerShell):**
```bash
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

Install all the necessary dependencies, including development tools like `pytest` and `moto`, using `uv`. The `-e` flag installs the project in "editable" mode.

```bash
uv pip install -e ".[dev]"
```

## Running the Application

### 1. Start Local DynamoDB

For local development, the application is configured to connect to a local DynamoDB instance. Run the following Docker command to start one.

```bash
docker run -p 8001:8000 amazon/dynamodb-local
```

Or you can run "NoSQL Workbench" and enable "DDB local" to start DynamoDB local, and change port to 8001.


### 2. Run the FastAPI Server

With the virtual environment activated and the database running, start the FastAPI application using `uvicorn`. The `--reload` flag will automatically restart the server when you make code changes.

```bash
uvicorn my_app.main:app --reload
```

You can now access the application:
-   **API Docs**: http://127.0.0.1:8000/docs
-   **Root URL**: http://127.0.0.1:8000/

## Running Tests

To run the unit tests, execute the `pytest` command in your terminal.

```bash
pytest
```

The tests use the `moto` library to mock AWS services, including DynamoDB. This means you **do not** need to have the Docker container for DynamoDB running to execute the tests.
