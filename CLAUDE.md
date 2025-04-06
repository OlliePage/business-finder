# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Install: `poetry install`
- Run all tests: `poetry run pytest`
- Run single test file: `poetry run pytest tests/test_file.py`
- Run single test: `poetry run pytest tests/test_file.py::test_function_name`

## Code Style Guidelines
- **Formatting**: 4-space indentation, ~80-100 chars per line
- **Imports**: Standard library first, third-party second, local modules last
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error Handling**: Use try/except with specific exceptions; log errors; return None on API errors
- **Documentation**: Use double quotes for docstrings
- **Structure**: Keep code modular in appropriate directories (api/, exporters/, etc.)
- **Types**: Currently no type annotations (future improvement)

## Project Structure
Business finder is a Python tool that helps locate and export business information using external APIs.