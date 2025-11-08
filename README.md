# LifeLine - Personal Memory & Timeline Assistant

A personal AI agent built with the **OpenAI Agents SDK** that helps you capture, organize, and reflect on the meaningful moments of your life.

## Interfaces

- **CLI**: Beautiful interactive terminal interface with autocomplete and rich formatting
- **Web**: Clean, mobile-friendly web interface with real-time chat ([Quick Start](WEB_QUICKSTART.md))

## Features

- **Timeline Logging**: Record life events with natural language
- **Smart Categorization**: Automatically organize events by category (career, travel, health, personal, learning, social, milestone, creative, financial)
- **Intelligent Queries**: Retrieve memories by date range, category, or search terms
- **Reflective Insights**: Get meaningful summaries and pattern recognition
- **Persistent Memory**: All conversations and timeline data stored locally in SQLite
- **MCP Integration**: Basic MCP server for future timeline visualization tools
- **Beautiful CLI**: Interactive terminal interface with rich formatting
- **Web Interface**: Real-time chat with WebSocket, mobile-first responsive design

## Architecture

Built using the OpenAI Agents SDK:
- **Agent**: LifeLine agent with warm, empathetic personality
- **Tools**: 9 function tools for timeline operations
- **Session**: SQLiteSession for persistent conversation memory
- **Database**: Separate SQLite database for timeline events
- **MCP**: Model Context Protocol server for external integrations

## Installation

### Prerequisites

- Python 3.10 or higher
- [UV](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

### Setup with UV (Recommended)

UV is a fast Python package manager. Install it first if you haven't:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then set up LifeLine:

```bash
# Clone or download this repository
cd agentsdk

# Create virtual environment and install dependencies
uv sync

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'

# Run LifeLine
uv run python main.py
```

### Alternative Setup with pip

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'

# Run LifeLine
python main.py
```

## Usage

### Web Interface (Recommended)

For a beautiful, mobile-friendly experience, use the web interface:

```bash
# Terminal 1: Start the backend
make web

# Terminal 2: Start the frontend
cd web-ui && npm run dev
```

Then open `http://localhost:3000` in your browser.

See [WEB_QUICKSTART.md](WEB_QUICKSTART.md) for detailed instructions.

### Interactive CLI

Start the LifeLine assistant in terminal:

```bash
# With UV
uv run python main.py

# Or with standard Python
python main.py

# Or use make
make run
```

### Example Interactions

**Log a memory:**
```
You: Log: Had coffee with Sarah at the new Italian cafe downtown
LifeLine: Event logged successfully! [ID: 1] 'Coffee with Sarah' added to social category at 2025-01-14T15:30
```

**Query by date:**
```
You: What did I do in December 2024?
LifeLine: [Retrieves and summarizes December events]
```

**Search by category:**
```
You: Show my travel memories
LifeLine: [Lists all travel-category events with details]
```

**Get statistics:**
```
You: /stats
[Displays total events, categories breakdown, and timeline range]
```

### CLI Commands

- `/help` or `/h` - Show help message
- `/quit` or `/exit` - Exit LifeLine
- `/stats` or `/s` - Show timeline statistics
- `/clear` or `/c` - Clear conversation history (keeps timeline data)
- `/categories` or `/cat` - List all categories with event counts
- `/recent [N]` or `/r [N]` - Show recent events (default: 10)
- `/search <query>` or `/find <query>` - Search events by keyword

**CLI Features:**
- **Tab completion** - Press `Tab` to autocomplete commands
- **Command history** - Use `↑/↓` arrows to navigate previous commands
- **Auto-suggestions** - See command suggestions as you type
- **Fuzzy matching** - Commands work with aliases and partial matches

## Project Structure

```
lifeline/
├── lifeline/                  # Main package
│   ├── __init__.py           # Package initialization
│   ├── agent.py              # LifeLine agent definition
│   ├── tools.py              # Function tools for timeline operations
│   ├── models.py             # Pydantic models for data validation
│   ├── database.py           # SQLite database operations
│   └── mcp_server.py         # MCP server for timeline visualization
├── main.py                    # CLI entry point
├── examples/                  # Example scripts
│   └── example_usage.py      # Programmatic usage examples
├── docs/                      # Documentation
│   ├── QUICKSTART.md         # Quick start guide
│   └── AGENTS.md             # Contributor guidelines
├── data/                      # Data directory (auto-created)
│   ├── lifeline.db           # Timeline events database (auto-created)
│   └── lifeline_user.db      # Conversation history (auto-created)
└── requirements.txt           # Dependencies
```

## Using as a Python Module

You can also import and use LifeLine in your own Python code:

```python
import asyncio
from agents import Runner, SQLiteSession
from lifeline.agent import create_lifeline_agent

async def use_lifeline():
    # Create agent
    agent = create_lifeline_agent("my_timeline.db")

    # Create session for conversation memory
    session = SQLiteSession("user_123", "conversations.db")

    # Run agent
    result = await Runner.run(
        agent,
        "Log: Started learning Python today in the learning category",
        session=session
    )

    print(result.final_output)

asyncio.run(use_lifeline())
```

## Database Schema

Timeline events are stored in SQLite with the following schema:

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'personal',
    timestamp TEXT NOT NULL,  -- ISO format
    tags TEXT,  -- JSON array
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## MCP Integration

LifeLine supports the Model Context Protocol (MCP) through the OpenAI Agents SDK's built-in `agents.mcp` module.

### Exporting Timeline Data

Export your timeline to JSON for external tools:

```bash
# With UV
uv run python -m lifeline.mcp_server

# Or with standard Python
python -m lifeline.mcp_server data/lifeline.db data/timeline_export.json
```

This creates a JSON file with all your events, categories, and statistics.

### Using LifeLine with MCP Servers

Connect LifeLine to external MCP servers (filesystem, Git, etc.):

```python
from agents import Runner
from agents.mcp import MCPServerStdio
from lifeline.agent import create_lifeline_agent
from pathlib import Path

async def lifeline_with_files():
    # Connect to filesystem MCP server
    docs_dir = Path("/path/to/your/documents")

    async with MCPServerStdio(
        name="Filesystem Server",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(docs_dir)]
        }
    ) as server:
        # Create agent with both LifeLine tools AND filesystem access
        agent = create_lifeline_agent("data/lifeline.db")
        agent.mcp_servers = [server]

        # Now agent can read files AND manage timeline
        result = await Runner.run(
            agent,
            "Read my journal.txt and log important events to my timeline"
        )
        print(result.final_output)
```

### Integration Ideas

Use LifeLine with MCP for:
- **Filesystem integration** - Scan journal files and auto-log events
- **Git integration** - Track project milestones from commit history
- **Calendar sync** - Export timeline to calendar apps
- **Data visualization** - Build dashboards using exported JSON
- **Markdown export** - Generate timeline reports

## Function Tools

LifeLine agent has access to these tools:

### Date & Time Tools
1. **get_todays_date()** - Get today's date (agent uses this first for any time-related requests)
2. **get_current_datetime()** - Get current date and time with readable format
3. **calculate_future_date(days)** - Calculate a future date by adding days to today
4. **parse_relative_date()** - Convert "yesterday", "last week" to ISO dates

### Timeline Management
5. **log_event()** - Add new timeline entry with title, description, category, timestamp
6. **query_events_by_date()** - Retrieve events in date range
7. **query_events_by_category()** - Filter by category
8. **search_events()** - Full-text search in titles and descriptions
9. **get_recent_events()** - Get latest N events
10. **get_all_categories()** - List all categories in use
11. **get_timeline_statistics()** - Overall stats (total events, categories, date range)

### Reminder System
12. **set_reminder()** - Create a reminder for a future task (stored in timeline with 'reminder' category)
13. **get_upcoming_reminders()** - Show reminders due in the next X days

### Web Search (Placeholder)
14. **search_web()** - Placeholder for web search integration (not yet connected to live search)

## Categories

Default categories include:
- **career** - Job changes, promotions, projects
- **travel** - Trips, vacations, places visited
- **health** - Medical events, fitness, wellness
- **personal** - General life events
- **learning** - Courses, skills, books, insights
- **social** - Friends, family, relationships
- **milestone** - Major life events
- **creative** - Art, writing, creative projects
- **financial** - Purchases, investments, goals
- **reminder** - Future tasks and reminders (auto-created by set_reminder tool)

Users can create custom categories by simply mentioning them.

## Reminder System

LifeLine now includes a built-in reminder system! Reminders are stored as timeline events with the 'reminder' category.

**Setting reminders:**
```
You: Remind me to cancel Netflix in 10 days
LifeLine: [Gets today's date, calculates future date, sets reminder]
"I've set a reminder to cancel Netflix on November 18, 2025 (Monday) - that's 10 days from today!"
```

**Viewing reminders:**
```
You: What are my upcoming reminders?
LifeLine: [Shows all reminders with due dates]
```

**How it works:**
- Agent uses `get_todays_date()` to know the current date
- Agent uses `calculate_future_date(days)` to calculate the due date
- Agent uses `set_reminder()` to create the reminder
- Reminders are stored in the timeline and can be queried like any other event

## Error Handling

LifeLine includes friendly error handling:
- Invalid dates are handled gracefully
- Database errors show helpful messages
- Tool failures don't crash the conversation
- All data operations include try-catch blocks

## Privacy & Data

- All data stored **locally** in SQLite databases
- No data sent anywhere except OpenAI for agent processing
- Conversation history in `data/lifeline_user.db`
- Timeline events in `data/lifeline.db`
- Both databases are portable and can be backed up

## Extending LifeLine

### Adding Custom Tools

Add new tools in `lifeline/tools.py`:

```python
@function_tool
def my_custom_tool(param: str) -> str:
    """Your tool description."""
    # Your implementation
    return "Result"

# Add to ALL_TOOLS list
```

### Custom Categories

Simply mention new categories when logging:

```
You: Log: Published my first blog post in the blogging category
```

### Integrating with External Systems

Use the MCP server to connect LifeLine to:
- Notion, Obsidian, or other note-taking apps
- Calendar applications
- Habit tracking tools
- Custom visualization dashboards

## Development

### Setting Up Dev Environment

```bash
# With UV (installs dev dependencies automatically)
uv sync

# Or use the Makefile
make install

# With pip
pip install -e ".[dev]"
```

### Makefile Commands

For convenience, common commands are available via Make:

```bash
make help          # Show all available commands
make install       # Install dependencies
make run           # Run LifeLine CLI
make example       # Run example usage
make export        # Export timeline data to JSON
make test          # Run tests
make format        # Format code
make lint          # Lint code
make type-check    # Type check
make quality       # Run all quality checks
make clean         # Clean generated files
```

### Running Tests

```bash
# With UV
uv run pytest

# With standard Python
pytest tests/
```

### Code Quality Tools

```bash
# Format code with Black
uv run black lifeline/ main.py

# Lint with Ruff
uv run ruff check lifeline/ main.py

# Type checking with mypy
uv run mypy lifeline/

# Run all quality checks
uv run black lifeline/ && uv run ruff check lifeline/ && uv run mypy lifeline/
```

### Code Standards

The codebase follows:
- Type hints throughout
- Pydantic models for validation
- Async/await patterns
- Clear docstrings
- Error handling
- Black formatting (100 char line length)
- Ruff linting rules

## Troubleshooting

**Issue: "Database not initialized" error**
- Solution: Make sure `init_tools()` is called before using tools

**Issue: Agent not using tools**
- Solution: Check that your OpenAI API key is set and valid

**Issue: Dates not parsing correctly**
- Solution: Use ISO format (YYYY-MM-DD) or relative terms like "today", "yesterday"

## Future Enhancements

Potential additions:
- Reminder system with notifications
- Export timeline to markdown, PDF, or iCal
- Advanced visualization dashboard
- Photo attachments for events
- Recurring event patterns
- Goal tracking and progress monitoring
- AI-generated reflections and insights
- Voice input for logging events
- Mobile companion app

## Contributing

This is a personal project template, but feel free to:
- Fork and customize for your needs
- Add new features
- Create visualization tools using the MCP server
- Share your extensions

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

Built with:
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) - Agent framework with built-in MCP support
- [Rich](https://github.com/Textualize/rich) - Beautiful CLI output
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation

## Support

For issues with:
- **LifeLine**: Check the code and modify as needed
- **OpenAI Agents SDK**: See [official documentation](https://github.com/openai/openai-agents-python)
- **OpenAI API**: Check [OpenAI status](https://status.openai.com)

---

**Start preserving your life's meaningful moments with LifeLine today!**
