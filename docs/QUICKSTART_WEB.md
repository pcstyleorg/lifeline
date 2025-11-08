# LifeLine Web UI - Quick Start

Get the web UI up and running in 3 minutes.

## Prerequisites

- Python 3.10+
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

## Installation & Run

### Step 1: Install Dependencies
```bash
uv sync
```

### Step 2: Start the Web Server
```bash
make web
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 3: Open in Browser
```
http://localhost:8000
```

That's it! You're ready to use LifeLine.

## First Steps

### Log Your First Memory
1. In the chat box at the bottom, type:
   ```
   I just finished reading an amazing book today!
   ```
2. Press Enter and watch the agent respond

### View Your Timeline
1. Click the **📅 Timeline** button in the sidebar
2. Your memory appears in chronological order
3. Use the category filter to find specific types of events

### Check Your Statistics
1. Click the **📊 Statistics** button
2. See your memory patterns and category breakdown

### Set a Reminder
1. In chat, type:
   ```
   Remind me to call my dentist in 14 days
   ```
2. The agent will set a reminder for you

## Chat Examples

Try these natural language inputs:

**Logging Events:**
- "Log: I got promoted today!"
- "Started learning Python"
- "Visited Tokyo for a week"

**Querying the Past:**
- "What did I do in December?"
- "Show my health-related events"
- "Find memories about coffee"

**Managing Reminders:**
- "Remind me to renew my passport in 30 days"
- "Set a reminder for my mom's birthday"
- "Show my upcoming reminders"

**Getting Insights:**
- "What were my major accomplishments this year?"
- "How many travel memories do I have?"
- "What's been my most active category?"

## Keyboard Shortcuts

- **Enter** - Send message
- **Shift + Enter** - (future: new line in message)
- **Tab** - Autocomplete (in category filter)

## Features Overview

### 💬 Chat
- Natural language conversation
- Real-time responses
- Context-aware replies
- Warm, empathetic tone

### 📅 Timeline
- Browse all memories chronologically
- Filter by category
- View event details
- See tags and metadata

### 📊 Statistics
- Total memory count
- Timeline date range
- Category distribution
- Visual charts

## Tips & Tricks

1. **Be Specific**: More detail = better memories
   ```
   ✅ Good: "I finished a 5K run in 28 minutes today!"
   ❌ Vague: "I ran"
   ```

2. **Use Categories**: Help organize your memories
   - career, travel, health, personal, learning, social, milestone, creative, financial, reminder

3. **Add Context**: The agent learns from your story
   ```
   "Started my new job at TechCorp in San Francisco.
    Very excited about the opportunity!"
   ```

4. **Ask Follow-ups**: Have natural conversations
   ```
   You: "I went hiking yesterday"
   LifeLine: [logs with details]
   You: "What was the weather like?"
   LifeLine: [can reference previous context]
   ```

5. **Manage Dates**: Use natural language
   - "in 5 days"
   - "next Monday"
   - "2 weeks from now"
   - "tomorrow"

## Troubleshooting

### "Connection lost" Message
1. Verify server is running: `make web`
2. Check http://localhost:8000 in browser
3. Refresh the page (Cmd/Ctrl + R)

### No Response from Agent
1. Verify `OPENAI_API_KEY` is set:
   ```bash
   echo $OPENAI_API_KEY
   ```
2. Check server logs for errors
3. Restart: `Ctrl+C` and `make web` again

### Database Issues
1. Reset everything (deletes all data!):
   ```bash
   rm data/*.db
   make web
   ```

## Accessing from Other Devices

The web server runs on `0.0.0.0:8000`, so you can access it from other machines on your network:

```
http://<your-machine-ip>:8000
```

Find your machine IP:
- **Mac/Linux**: `ifconfig | grep inet`
- **Windows**: `ipconfig`

## Stop the Server

Press `Ctrl+C` in the terminal running the server.

## Next Steps

1. **Try All Features**: Explore chat, timeline, and stats
2. **Build Your History**: Log several memories
3. **Customize**: Edit `web/static/style.css` for your brand colors
4. **Share**: Share your IP/port with others to let them access your LifeLine
5. **Deploy**: Host on cloud platform (Heroku, Railway, etc.)

## Documentation

- **Full Guide**: See `WEB_UI_README.md`
- **Implementation Details**: See `WEB_UI_SUMMARY.md`
- **Project Overview**: See `CLAUDE.md`
- **CLI Alternative**: Run `python main.py` for terminal interface

## Getting Help

1. Check the Troubleshooting section above
2. Review browser console (F12 → Console tab)
3. Check server logs in terminal
4. Read full documentation in `WEB_UI_README.md`

---

**Ready?** Start the server with `make web` and open http://localhost:8000!
