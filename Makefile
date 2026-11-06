# Everyday commands. `make` lists them. `make check` runs exactly what CI runs.

.DEFAULT_GOAL := help
.PHONY: help sync check lint typecheck test format

help:  ## list the commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-z-]+:.*## / {printf "  make %-10s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sync:  ## install the locked dependencies into .venv
	uv sync --locked

check: lint typecheck test  ## lint, type-check and test (the CI gate)

lint:  ## ruff lint and format check
	uv run ruff check .
	uv run ruff format --check .

typecheck:  ## mypy (strict) on src/
	uv run mypy src

test:  ## pytest
	uv run pytest

format:  ## apply ruff formatting and safe fixes
	uv run ruff check --fix .
	uv run ruff format .
