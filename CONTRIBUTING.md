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

## Publishing

Publishing uses PyPI Trusted Publishing from GitHub Actions. Configure a PyPI
publisher for:

- owner: `spokenforms`
- repository: `spokenforms`
- workflow: `publish.yml`
- environment: `pypi`

Then publish by creating a GitHub Release, or by running the `Publish` workflow
manually with `publish-to-pypi` as the confirmation input.
