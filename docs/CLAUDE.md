# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LifeLine** is a personal memory & timeline assistant built with the OpenAI Agents SDK. It helps users capture, organize, and reflect on meaningful moments in their lives through:
- Natural language event logging (with automatic categorization)
- Timeline queries by date, category, or search
- Reminder management with proper date calculations
- Persistent SQLite storage for conversations and timeline events

## Quick Start Commands

Use these commands frequently:

```bash
# Development setup
uv sync              # Install dependencies

# Running the application
uv run python main.py              # Start interactive CLI
uv run python example_usage.py     # Run demonstration examples

# Code quality
make format          # Format with Black (line-length: 100)
make lint            # Lint with Ruff
make type-check      # Type check with mypy
make quality         # Run all checks (format + lint + type-check)

# Testing & debugging
uv run pytest                                # Run all tests
uv run pytest -s -k <test_name>            # Run specific test with output
uv run pytest tests/test_timeline.py        # Run single test file

# Data export
uv run python -m lifeline.mcp_server        # Export timeline to JSON
```

## Architecture & Key Components

### Core Agent System
- **`lifeline/agent.py`**: Defines the LifeLine agent with comprehensive instructions including:
  - **CRITICAL date handling rules**: Agent MUST call `get_todays_date()` FIRST before any time-related operation
  - Warm, empathetic personality configured via instructions
  - 14 function tools integrated for memory and reminder operations
  - Uses OpenAI Agents SDK with `gpt-4o` model

### Data Layer
- **`lifeline/database.py`**: `TimelineDatabase` class managing SQLite operations
  - Auto-creates schema with indexed tables for fast queries
  - Methods: `insert_event()`, `query_events()`, `get_recent_events()`, `get_category_stats()`
  - All date operations use ISO format strings
  - Supports filtering by date range, category, tags, and text search

- **`lifeline/models.py`**: Pydantic models for type safety
  - `TimelineEvent`: Single timeline entry with validation
  - `EventQuery`: Query parameters with optional filters
  - `EventSummary`: Response summaries for agent output
  - All models auto-normalize categories and tags to lowercase

### Tool System
- **`lifeline/tools.py`**: 14 `@function_tool` decorated functions the agent calls
  - **Date Tools** (CRITICAL):
    - `get_todays_date()`: Returns readable date with day of week - **MUST be called first**
    - `calculate_future_date(days)`: Adds days to today (for "remind me in X days")
    - `parse_relative_date()`: Converts "yesterday", "last week" to ISO dates
    - `get_current_datetime()`: Returns ISO + readable format
  - **Timeline Tools**:
    - `log_event()`: Creates entry with proper timestamp calculation
    - `query_events_by_date/category()`: Filtered retrieval
    - `search_events()`: Full-text search in titles/descriptions
    - `get_recent_events()`, `get_all_categories()`, `get_timeline_statistics()`
  - **Reminder Tools**:
    - `set_reminder()`: Creates reminder as timeline event with 'reminder' category
    - `get_upcoming_reminders()`: Shows reminders due in next N days
  - All tools use global `_db` initialized via `init_tools(db_path)`

### CLI Interface
- **`main.py`**: Interactive REPL using Rich for beautiful output
  - `SQLiteSession` persists conversation history across runs
  - Special commands: `/quit`, `/stats`, `/clear`, `/help`, `/voice` (for future voice mode)
  - Uses `Prompt.ask()` for input, `console.print()` for output
  - Async/await pattern with `asyncio.run()`

### MCP Integration
- **`lifeline/mcp_server.py`**: Data export and MCP integration
  - `TimelineDataExporter`: Exports timeline to JSON for external tools
  - Example code for connecting to external MCP servers (filesystem, git, etc.)
  - Can be extended for real MCP server implementation

### Examples & Testing
- **`example_usage.py`**: Demonstrates all features including reminder system
- **`pyproject.toml`**: UV/pip configuration with Black, Ruff, mypy settings

## Critical Implementation Details

### Date Handling (MOST IMPORTANT)
The agent instruction set includes explicit rules that **MUST be enforced**:

1. **Agent ALWAYS calls `get_todays_date()` FIRST** for any time reference
2. **Never assume dates** - always use tools
3. **For future dates**: Use `calculate_future_date(days)` after getting today
4. Example: "Remind me in 10 days to cancel Netflix"
   - First: `get_todays_date()` → "2025-11-08"
   - Then: `calculate_future_date(10)` → "2025-11-18"
   - Then: `set_reminder(due_date="2025-11-18")`

### Session & Persistence
- **Conversation Memory**: `SQLiteSession(session_id, db_path)` automatically loads history
- **Timeline Data**: Separate SQLite database `lifeline.db` for events
- **Reminders**: Stored as timeline events with `category="reminder"`

### Agent Tool Integration
- Tools are added via `ALL_TOOLS` list in `tools.py`
- Each tool must have proper Pydantic-style `Annotated` type hints for descriptions
- Agent instructions explain when and how to use each tool
- Tool outputs are strings/dicts that agent includes in responses

### Event Categories
Standard: career, travel, health, personal, learning, social, milestone, creative, financial, reminder
Custom categories auto-created by agent based on user input

## Development Patterns

### Adding New Tools
1. Create `@function_tool` in `lifeline/tools.py` with clear docstring and Annotated params
2. Add to `ALL_TOOLS` list at bottom of file
3. Update agent instructions in `lifeline/agent.py` to explain when/how to use tool
4. Test via `example_usage.py` with multi-turn conversation

### Modifying Agent Behavior
- Edit `LIFELINE_INSTRUCTIONS` string in `lifeline/agent.py`
- Focus on the **CRITICAL: Date Handling Rules** section - it's carefully designed
- Ensure instructions explain tool usage clearly
- Test with example conversations

### Database Queries
- Use `EventQuery` model for filtering (handles None values)
- All timestamps are ISO format strings (YYYY-MM-DDTHH:MM:SS)
- Indexed on category and timestamp for performance
- Tags are JSON arrays stored as text

### Testing
- Tests should use `example_timeline.db` (separate from production `lifeline.db`)
- Use `pytest-asyncio` for async test functions
- Mock OpenAI API calls or use environment variable `OPENAI_API_KEY`

## Code Quality Standards

- **Formatting**: Black (100 char line length)
- **Linting**: Ruff with isort integration
- **Type Hints**: All functions must have return types (`disallow_untyped_defs`)
- **Async**: Use `async/await` throughout; `asyncio.run()` at entry point
- **Error Handling**: Graceful fallbacks with friendly messages to user

Run `make quality` before committing.

## Planned Features

### Voice Mode (In Development)
- Use `VoicePipeline` from `agents.voice` module
- Wrap existing agent with `SingleAgentVoiceWorkflow`
- All 14 tools work seamlessly with voice input/output
- Dependencies: `openai-agents[voice]`, `sounddevice`, `numpy`

### Web Search Integration
- `search_web()` tool is a placeholder
- Will integrate with actual web search when needed

### RealtimeAgent for Phone Calls
- Alternative to VoicePipeline for continuous Twilio/phone integration
- Uses `agents.realtime.RealtimeAgent` + `RealtimeRunner`
- Same tools and instructions work seamlessly

## File Locations
- User database: `lifeline.db` (timeline events)
- Session history: `lifeline_user.db` (conversation)
- Examples: `example_usage.py` (runnable demonstrations)
- Tests: `tests/` (pytest test files)
- Output exports: `timeline_export.json` (via `make export`)

## OpenAI SDK Integration Notes

- Using **OpenAI Agents SDK** (not base OpenAI library)
- Package name: `openai-agents` (not `openai-agents-python`)
- `Agent` class with `tools` parameter and `SQLiteSession` for persistence
- `Runner.run()` with `max_turns=10` for multi-step tool invocation
- Built-in MCP support via `agents.mcp` module

## Common Debugging

**Issue**: Agent not using tools
- Check `OPENAI_API_KEY` is set
- Verify tool is in `ALL_TOOLS` list
- Check tool docstring and parameter annotations are clear

**Issue**: Reminders have wrong dates
- Verify agent calls `get_todays_date()` first
- Check `calculate_future_date()` output before `set_reminder()`
- Look at agent instructions for date handling rules

**Issue**: Past data missing from queries
- Check `lifeline.db` exists and has data via `make export`
- Verify date range queries use correct ISO format
- Check SQLiteSession is loading previous conversations

