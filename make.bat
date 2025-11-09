@echo off

if "%1"=="test" (
    uv run pytest
    goto :eof
)

if "%1"=="setup" (
    uv venv --clear
    uv pip install -e ".[dev]"
    goto :eof
)

if "%1"=="clean" (
    rmdir /s /q .venv 2>nul
    rmdir /s /q __pycache__ 2>nul
    rmdir /s /q .pytest_cache 2>nul
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
    goto :eof
)

if "%1"=="lint" (
    uv run ruff check --fix .
    goto :eof
)

if "%1"=="run" (
    uv run uvicorn my_app.main:app --reload
    goto :eof
)

echo Usage: make.bat [test^|setup^|clean^|lint^|run]