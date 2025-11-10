.PHONY: test setup clean lint run

test:
	uv sync --extra dev
	uv run pytest

setup:
	uv venv --clear
	uv pip install -e ".[dev]"

clean:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
    rm -rf .mypy_cache
	rm -rf src/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	uv run ruff check --fix .

run:
	uv run uvicorn my_app.main:app --reload