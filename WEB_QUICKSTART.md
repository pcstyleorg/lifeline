# LifeLine Web - Quick Start Guide

A clean, simple, and mobile-friendly web interface for LifeLine built with Next.js and FastAPI.

## Architecture

- **Backend**: FastAPI with WebSocket support (Python)
- **Frontend**: Next.js 16 + Tailwind CSS v4 (TypeScript/React)
- **Database**: Shared SQLite database with CLI (`data/lifeline.db`)
- **Communication**: WebSocket for real-time chat, REST API for data queries

## Features

- 🎯 Clean, minimal chat interface
- 📱 Mobile-first responsive design
- ⚡ Real-time AI responses via WebSocket
- 🔄 Auto-reconnection on connection loss
- 💬 Markdown support in messages
- 🎨 Beautiful UI with Tailwind CSS v4
- 🔗 Shared database with CLI

## Prerequisites

- Python 3.10+
- Node.js 18+
- UV package manager (recommended) or pip
- OpenAI API key

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
make install
# or: uv sync
```

### 2. Set OpenAI API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Start the Backend Server

In terminal 1:

```bash
make web
# or: uv run uvicorn web:app --reload --port 8000
```

The FastAPI server will start at `http://localhost:8000`

### 4. Start the Frontend

In terminal 2:

```bash
cd web-ui
npm run dev
```

The Next.js app will start at `http://localhost:3000`

### 5. Open in Browser

Visit `http://localhost:3000` and start chatting with LifeLine!

## Usage

### Chat Interface

- Type messages in the input field at the bottom
- Press **Enter** to send (Shift+Enter for new line)
- The AI will respond in real-time via WebSocket
- Messages are displayed in a clean, mobile-friendly layout

### Quick Actions

On the welcome screen, you can:
- Ask "What can you do?" to learn about features
- Log an event with example prompts
- View recent events
- Check timeline statistics

### Example Queries

- "Log: I started learning Python today"
- "What did I do last week?"
- "Show my travel memories"
- "Show me my timeline statistics"
- "What are my recent events?"

## API Endpoints

### REST API

- `GET /` - Health check
- `GET /api/stats` - Get timeline statistics
- `GET /api/events/recent?limit=10` - Get recent events
- `GET /api/categories` - Get all categories
- `POST /api/cleardb` - Clear all timeline data (dangerous!)

### WebSocket

- `ws://localhost:8000/ws/chat` - Real-time chat with LifeLine agent

**WebSocket Protocol:**

Client sends:
```json
{
  "message": "user message",
  "model": "gpt-4o"
}
```

Server sends:
```json
// Thinking indicator
{"type": "thinking"}

// Response message
{
  "type": "message",
  "content": "...",
  "timestamp": "2024-11-08T..."
}

// Error
{
  "type": "error",
  "error": "error message"
}
```

## Development

### File Structure

```
agentsdk/
├── web.py                    # FastAPI backend
├── web-ui/                   # Next.js frontend
│   ├── app/
│   │   ├── page.tsx         # Main chat page
│   │   ├── layout.tsx       # Root layout
│   │   ├── components/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── Header.tsx
│   │   │   └── ThinkingIndicator.tsx
│   │   └── hooks/
│   │       └── useWebSocket.ts
│   └── package.json
├── lifeline/                 # Shared backend logic
├── main.py                   # CLI interface
└── data/
    ├── lifeline.db          # Shared database
    └── lifeline_web_user.db # Web conversation history
```

### Backend Development

The FastAPI backend (`web.py`) reuses all the existing LifeLine components:
- `TimelineDatabase` for database operations
- `create_lifeline_agent()` for agent creation
- All the same tools and features as the CLI

### Frontend Development

The Next.js frontend is a simple, clean chat interface:
- **useWebSocket hook**: Manages WebSocket connection and state
- **ChatMessage**: Renders individual messages with timestamps
- **ChatInput**: Handles user input with keyboard shortcuts
- **Header**: Shows connection status
- **ThinkingIndicator**: Shows when AI is processing

### Styling

Uses Tailwind CSS v4 with mobile-first approach:
- Responsive breakpoints (sm, md, lg)
- Touch-friendly buttons and inputs
- Auto-resizing textarea
- Smooth animations and transitions

## Mobile Experience

The interface is optimized for mobile devices:
- ✅ Full-screen layout on mobile
- ✅ Touch-friendly input and buttons
- ✅ Responsive text sizing
- ✅ Proper viewport scaling
- ✅ Auto-scroll to latest message
- ✅ Keyboard-aware layout

## Production Deployment

### Backend (FastAPI)

Deploy using any Python hosting service:

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn web:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Next.js)

Deploy to Vercel (recommended):

```bash
cd web-ui
npm run build
vercel --prod
```

Or deploy to any Node.js hosting service.

### Environment Variables

**Backend:**
- `OPENAI_API_KEY` - Your OpenAI API key (required)

**Frontend:**
- Update `WS_URL` in `app/page.tsx` to your production backend URL

## Troubleshooting

### Backend won't start

```bash
# Make sure dependencies are installed
make install

# Check Python version
python --version  # Should be 3.10+

# Check if port 8000 is available
lsof -i :8000
```

### Frontend won't start

```bash
cd web-ui

# Clean and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

### WebSocket connection fails

- Make sure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings in `web.py`
- Check firewall/network settings

### Database issues

- Both CLI and web share the same database
- Database is auto-created on first run
- Location: `data/lifeline.db`
- To reset: use `/cleardb` command (with confirmation)

## Next Steps

- Customize the UI styling in components
- Add more API endpoints as needed
- Implement authentication (for multi-user)
- Add file upload for photos
- Create mobile PWA
- Add push notifications

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## Support

For issues or questions:
- Check the main README.md
- Review the WEB_UI documentation in docs/
- Open an issue on GitHub
