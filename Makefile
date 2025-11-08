.PHONY: help install run example export test format lint type-check clean

help:
	@echo "LifeLine - Available Commands"
	@echo "=============================="
	@echo "  make install      - Install dependencies with UV"
	@echo "  make run          - Run LifeLine CLI"
	@echo "  make example      - Run example usage script"
	@echo "  make export       - Export timeline data to JSON"
	@echo "  make test         - Run tests"
	@echo "  make format       - Format code with Black"
	@echo "  make lint         - Lint code with Ruff"
	@echo "  make type-check   - Type check with mypy"
	@echo "  make quality      - Run all quality checks"
	@echo "  make clean        - Remove generated files"

install:
	uv sync

run:
	uv run python main.py

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

type-check:
	uv run mypy lifeline/

quality: format lint type-check
	@echo "All quality checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*.db-journal data/*.db-wal data/*.db-shm
