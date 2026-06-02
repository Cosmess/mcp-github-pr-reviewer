.PHONY: install test lint format run docker-build docker-run

install:
	pip install -e ".[dev]"

test:
	python -m pytest

lint:
	python -m ruff check .

format:
	python -m ruff format .

run:
	mcp-github-pr-reviewer

docker-build:
	docker compose build

docker-run:
	docker compose run --rm mcp-github-pr-reviewer
