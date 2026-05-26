# Contributing

Use `uv` for development:

```bash
uv sync --all-extras --dev
uv run pre-commit install
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv build
```
