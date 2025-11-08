# Repository Guidelines

Contributor guide for the LifeLine project—a personal memory and timeline assistant built with the OpenAI Agents SDK.

## Project Structure & Module Organization

The repository follows a clear Python package structure:

```
lifeline/              # Main package directory
├── agent.py           # Agent definition and configuration
├── tools.py           # Function tools for timeline operations
├── database.py        # SQLite database operations
├── models.py          # Pydantic models for data validation
└── mcp_server.py      # MCP server for external integrations

main.py                # CLI entry point
examples/              # Example scripts
├── example_usage.py   # Example programmatic usage
data/                  # Data directory
├── lifeline.db        # Timeline events database (auto-created)
└── lifeline_user.db   # Conversation history (auto-created)
```

Source code lives in `lifeline/`, entry points are at the root level. Database files are created automatically on first run.

## Build, Test, and Development Commands

### Setup
```bash
make install      # Install dependencies with UV (recommended)
```

### Running
```bash
make run          # Run LifeLine CLI
make example      # Run example usage script
make export       # Export timeline data to JSON via MCP server
```

### Testing
```bash
make test         # Run pytest test suite
```

### Code Quality
```bash
make format       # Format code with Black (100 char line length)
make lint         # Lint code with Ruff
make type-check   # Type check with mypy
make quality      # Run all quality checks (format, lint, type-check)
```

### Cleanup
```bash
make clean        # Remove generated files (__pycache__, .db-journal, etc.)
```

All commands use `uv run` under the hood. For direct execution: `uv run python main.py` or `uv run pytest`.

## Coding Style & Naming Conventions

### Python Standards
- **Python 3.10+** required
- **Type hints** throughout—use `typing` annotations for function parameters and return types
- **Async/await** patterns for agent interactions
- **Pydantic models** for data validation (see `models.py`)
- **Docstrings** for all functions and classes

### Formatting & Linting
- **Black** with 100 character line length (configured in `pyproject.toml`)
- **Ruff** for linting (E, W, F, I, B, C4, UP rules)
- **mypy** for type checking (strict mode enabled)

### Naming Patterns
- **Functions**: `snake_case` (e.g., `get_todays_date()`, `log_event()`)
- **Classes**: `PascalCase` (e.g., `TimelineDatabase`, `TimelineEvent`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `LIFELINE_INSTRUCTIONS`)
- **Module-level variables**: `snake_case` with leading underscore for private (e.g., `_db`)

### Code Organization
- Group related functionality in modules (tools, database, models)
- Use `@function_tool` decorator for agent tools
- Initialize tools with `init_tools(db_path)` before agent creation
- Keep agent instructions in `agent.py` as module-level constants

## Testing Guidelines

### Test Structure
- Tests should live in a `tests/` directory (not yet created)
- Use `pytest` with `pytest-asyncio` for async tests
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Running Tests
```bash
uv run pytest              # Run all tests
uv run pytest tests/       # Run tests in specific directory
uv run pytest -v           # Verbose output
```

### Test Configuration
Configured in `pyproject.toml` with `asyncio_mode = "auto"` for async test support.

## Commit & Pull Request Guidelines

### Commit Messages
- Use clear, descriptive messages
- Start with a verb in imperative mood (e.g., "Add reminder system", "Fix date parsing bug")
- Include context when helpful (e.g., "Update agent instructions for date handling")

### Pull Request Requirements
- **Description**: Explain what changes and why
- **Scope**: Keep PRs focused on a single feature or fix
- **Testing**: Include tests for new functionality when applicable
- **Documentation**: Update README.md or relevant docs if behavior changes
- **Code Quality**: Ensure `make quality` passes before submitting

### Example PR Description
```markdown
## Summary
Adds reminder system with date calculation tools.

## Changes
- New `set_reminder()` and `get_upcoming_reminders()` tools
- Date calculation helpers (`get_todays_date()`, `calculate_future_date()`)
- Updated agent instructions for reminder handling

## Testing
- Manual testing with CLI
- Example usage script updated
```

## Agent-Specific Instructions

### Adding New Tools
1. Define function in `lifeline/tools.py` with `@function_tool` decorator
2. Add comprehensive docstring explaining when/how to use
3. Add to `ALL_TOOLS` list
4. Update agent instructions in `agent.py` if behavior changes

### Database Operations
- All database access goes through `TimelineDatabase` class
- Use Pydantic models (`TimelineEvent`, `EventQuery`) for type safety
- Handle SQLite errors gracefully with try/except blocks

### Agent Configuration
- Agent instructions live in `LIFELINE_INSTRUCTIONS` constant
- Model: `gpt-4o` with temperature `0.7`
- Tools are initialized via `init_tools(db_path)` before agent creation

## Development Workflow

1. **Setup**: Run `make install` to set up environment
2. **Develop**: Make changes following coding style guidelines
3. **Test**: Run `make quality` before committing
4. **Commit**: Write clear commit messages
5. **Submit**: Create PR with description and ensure quality checks pass

For questions or clarifications, refer to `README.md` for detailed project documentation.

