.PHONY: help install run web example export test format lint type-check clean clean-all build-cli build-web build-frontend build-all build-macos build-windows build-linux

PYTHON ?= python3

help:
	@echo "LifeLine - Available Commands"
	@echo "=============================="
	@echo "  make install      - Install dependencies with UV"
	@echo "  make run          - Run LifeLine CLI"
	@echo "  make web          - Run LifeLine Web Server"
	@echo "  make example      - Run example usage script"
	@echo "  make export       - Export timeline data to JSON"
	@echo "  make test         - Run tests"
	@echo "  make format       - Format code with Black"
	@echo "  make lint         - Lint code with Ruff"
	@echo "  make type-check   - Type check with mypy"
	@echo "  make quality      - Run all quality checks"
	@echo "  make clean        - Remove generated files"
	@echo "  make clean-all    - Remove all artifacts (including .venv)"

install:
	uv sync

run:
	uv run python main.py

web:
	uv run uvicorn web:app --reload --port 8000

example:
	uv run python examples/example_usage.py

export:
	uv run python -m lifeline.mcp_server

test:
	uv run pytest

format:
	uv run black lifeline/ main.py examples/

lint:
	uv run ruff check lifeline/ main.py examples/

.PHONY: build-cli
build-cli:
	$(PYTHON) -m scripts.build --component cli

.PHONY: build-web
build-web:
	$(PYTHON) -m scripts.build --component web

.PHONY: build-frontend
build-frontend:
	$(PYTHON) -m scripts.build --component frontend

.PHONY: build-all
build-all:
	$(PYTHON) -m scripts.build --component all

.PHONY: build-macos
build-macos:
	$(PYTHON) -m scripts.build --target macos --component all

.PHONY: build-windows
build-windows:
	$(PYTHON) -m scripts.build --target windows --component all

.PHONY: build-linux
build-linux:
	$(PYTHON) -m scripts.build --target linux --component all

type-check:
	uv run mypy lifeline/

quality: format lint type-check
	@echo "All quality checks passed!"

clean:
	@echo "Cleaning Python artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*.db-journal data/*.db-wal data/*.db-shm
	@echo "Cleaning build artifacts..."
	rm -rf build/ 2>/dev/null || true
	rm -rf dist/ 2>/dev/null || true
	find . -maxdepth 1 -name "*.spec" -type f -delete 2>/dev/null || true
	@echo "Cleaning frontend build..."
	rm -rf web-ui/.next 2>/dev/null || true
	rm -rf web-ui/.turbo 2>/dev/null || true
	@echo "Cleaning ruff cache..."
	rm -rf .ruff_cache/ 2>/dev/null || true
	@echo "Cleaning test installs..."
	find /tmp -maxdepth 1 -type d -name "lifeline-*" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"

clean-all: clean
	@echo "Cleaning virtual environment..."
	rm -rf .venv 2>/dev/null || true
	rm -f .env 2>/dev/null || true
	@echo "Deep clean complete!"
