# LifeLine Web UI

A clean, modern web interface for the LifeLine personal memory and timeline assistant.

## Features

- **💬 Chat Interface**: Talk naturally with the LifeLine agent to log memories and ask questions
- **📅 Timeline View**: Browse your events in chronological order with filtering
- **📊 Statistics Dashboard**: View insights about your timeline with category breakdowns
- **🔔 Reminders**: Set and manage reminders for important tasks
- **🏷️ Categories & Tags**: Organize memories with automatic categorization
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Real-time Updates**: WebSocket-based chat for instant responses

## Quick Start

### Install Dependencies

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```

### Run the Web Server

```bash
uv run python web.py
```

Or with uvicorn directly:

```bash
uvicorn web:app --reload --host 0.0.0.0 --port 8000
```

### Access the UI

Open your browser and navigate to:

```
http://localhost:8000
```

## Usage

### Chat View (Default)

The chat interface is your main way to interact with LifeLine:

- **Log an event**: "I got promoted today!" or "Log: Started a new project"
- **Ask about the past**: "What did I do in December?" or "Show my travel memories"
- **Set reminders**: "Remind me to call my mom in 5 days"
- **Search memories**: "Find events related to coffee"

The agent will:
- Understand your request naturally
- Ask clarifying questions if needed
- Remember context across the conversation
- Provide warm, empathetic responses

### Timeline View

Browse your complete timeline of memories:

- **Chronological display**: Events shown from newest to oldest
- **Filter by category**: Select from dropdown to see specific types of events
- **Event details**: View title, description, category, and tags
- **Date information**: Each event shows the exact date

### Statistics View

Get insights about your timeline:

- **Total events**: Count of all memories logged
- **Date range**: Span of your timeline
- **Categories**: Number of different categories used
- **Category breakdown**: Visual chart of events per category

## Project Structure

```
.
├── web.py                    # FastAPI backend server
├── web/
│   ├── index.html           # Main HTML page
│   └── static/
│       ├── style.css        # CSS styling
│       └── app.js           # JavaScript application logic
├── lifeline/
│   ├── agent.py            # LifeLine agent definition
│   ├── database.py         # SQLite database operations
│   ├── models.py           # Pydantic models
│   ├── tools.py            # Agent tools/functions
│   └── mcp_server.py       # MCP integration
├── data/
│   ├── lifeline.db         # Timeline events database
│   └── lifeline_web_user.db # Conversation history
└── main.py                  # CLI interface (alternative to web)
```

## API Endpoints

### Chat

- **POST `/api/chat`**: Send a message and get a response (HTTP)
- **WebSocket `/ws/chat`**: Real-time chat connection

### Data

- **GET `/api/stats`**: Get timeline statistics
- **GET `/api/events/recent`**: Get recent events (limit: 10-100)
- **GET `/api/events/categories`**: Get list of all categories

## Configuration

The web server uses these defaults:

- **Host**: `0.0.0.0` (accessible from any machine)
- **Port**: `8000`
- **Database**: `data/lifeline.db`
- **Session ID**: `lifeline_web_user`

To change these, edit the configuration section in `web.py`:

```python
DB_PATH = "data/lifeline.db"
SESSION_ID = "lifeline_web_user"
DATABASE_PATH = f"data/{SESSION_ID}.db"
```

## Data Storage

- **Timeline Events**: Stored in `data/lifeline.db` (SQLite)
- **Conversation History**: Stored in `data/lifeline_web_user.db` (SQLite)
- Both databases are created automatically on first run
- All data is stored locally - nothing is sent to external servers

## Development

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# Run all checks
make quality
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest -s -k <test_name>

# Run with coverage
uv run pytest --cov
```

### Hot Reload

The web server includes auto-reload. Any changes to `web.py` or the frontend files will automatically reload:

```bash
uv run python web.py
```

## Architecture

### Backend (FastAPI)

- **`web.py`**: FastAPI application with REST and WebSocket endpoints
- Uses OpenAI Agents SDK for agent functionality
- Async/await pattern for non-blocking operations
- Thread-based execution for agent runs (compatible with asyncio)

### Frontend (Vanilla JS + CSS)

- **`index.html`**: Single-page application structure
- **`style.css`**: Clean, modern design with dark mode ready
- **`app.js`**: Client-side logic for chat, timeline, and statistics
- WebSocket connection for real-time updates
- Responsive grid layout with sidebar navigation

### Data Layer

- **SQLite database**: Fast, reliable local storage
- **Pydantic models**: Type-safe data handling
- **Indexed queries**: Quick filtering by date and category

## Troubleshooting

### WebSocket Connection Issues

If you see "Connection lost" messages:

1. Check that the server is running on port 8000
2. Verify no firewall is blocking port 8000
3. Try refreshing the browser page
4. Check browser console (F12) for errors

### Agent Not Responding

If messages aren't getting responses:

1. Verify `OPENAI_API_KEY` environment variable is set
2. Check that the database file is writable
3. Look at server logs for error messages
4. Restart the server

### Database Issues

If you want to reset the timeline:

```bash
rm data/lifeline.db data/lifeline_web_user.db
```

This will delete all data and create fresh empty databases.

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Initial page load: < 1 second
- Chat message: < 2-5 seconds (depends on agent processing)
- Timeline load: < 500ms for 100 events
- Optimized database queries with indexing

## Future Enhancements

Potential improvements:

- [ ] Dark mode toggle
- [ ] Export timeline to PDF/CSV
- [ ] Advanced search and filtering
- [ ] Tag management interface
- [ ] Event editing and deletion
- [ ] Collaborative sharing
- [ ] Calendar view
- [ ] Voice input support
- [ ] Mobile app
- [ ] Cloud sync option

## License

MIT - Same as the main LifeLine project

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the CLAUDE.md for project guidelines
3. Open an issue on the project repository
4. Check the main CLI interface (`python main.py`) for comparison

## Related

- **CLI Interface**: `python main.py` - Terminal-based interface
- **MCP Server**: `uv run python -m lifeline.mcp_server` - Data export
- **Main Documentation**: `CLAUDE.md` - Project overview
