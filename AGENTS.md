# Development Rules

## Project Context
This project uses the `uv` package manager and `pyproject.toml` for dependency management and configuration. The target Python version is 3.13. All commands must be run within the `uv` managed environment.

## Agent Instructions
When working on this project, the agent **MUST** adhere to the following rules:

- **ALWAYS** use `uv run <command>` instead of invoking `python`, `pytest`, or other tools directly.
- **NEVER** use `pip` or `pip3` for installing or managing packages.
- **ALWAYS** run `uv sync` to install/update dependencies after changes to `pyproject.toml`.
- **ALWAYS** run quality checks (`format`, `lint`, `typecheck`, `test`) before proposing any changes.
- **MAINTAIN** existing code formatting and style, primarily enforced by `ruff` and `mypy`.

## Useful Commands (for the AI Agent)

- **Install dependencies**: `uv sync`
- **Run a script**: `uv run python script.py`
- **Run tests**: `uv run pytest`
- **Run linting**: `uv run ruff check .`
- **Format code**: `uv run ruff format .`
- **Run type checking**: `uv run mypy`
- **Add a new package**: `uv add <package-name>`
- **Remove a package**: `uv remove <package-name>`
- **Create a virtual environment** (if needed): `uv venv`

## Project Structure
- `src/`: Contains all application-level code.
- `tests/`: Contains all unit and integration tests (using `pytest`).
- `pyproject.toml`: The main configuration and dependency file.
- `AGENTS.md`: This file, providing context and instructions.
