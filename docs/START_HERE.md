# LifeLine Web UI - START HERE

Welcome! You now have a beautiful web interface for the LifeLine personal memory assistant.

## 🚀 Get Started in 30 Seconds

### Step 1: Install
```bash
cd /Users/pcstyle/agentsdk
uv sync
```

### Step 2: Run
```bash
make web
```

### Step 3: Open Browser
Visit: **http://localhost:8000**

That's it! You're ready to start logging memories.

---

## 💡 What You Can Do

### 📝 Log Memories
```
You: "I completed my first marathon today!"
LifeLine: [Saves event, asks follow-up questions, logs with categories]
```

### 📅 Browse Timeline
- See all your memories in chronological order
- Filter by category (career, travel, health, etc.)
- View event details with tags and descriptions

### 🔔 Set Reminders
```
You: "Remind me to renew my passport in 30 days"
LifeLine: [Creates reminder for Dec 8]
```

### 📊 View Statistics
- Total events logged
- Timeline date range
- Category breakdown with visual charts

---

## 📚 Documentation

| Document | Read Time | What It Covers |
|----------|-----------|---|
| **QUICKSTART_WEB.md** | 5 min | Get started + examples |
| **WEB_UI_README.md** | 15 min | Complete guide + API |
| **WEB_UI_FEATURES.md** | 10 min | UI components + colors |
| **WEB_UI_SUMMARY.md** | 10 min | Architecture + decisions |
| **WEB_UI_OVERVIEW.txt** | 10 min | Everything at a glance |

**Start with:** `QUICKSTART_WEB.md`

---

## 🎯 First Steps

### 1. Log Something
Try this in the chat box:
```
"I just started learning web development today!"
```

### 2. View Timeline
Click **📅 Timeline** in the sidebar to see your event.

### 3. Check Stats
Click **📊 Statistics** to see your timeline patterns.

### 4. Set a Reminder
Try:
```
"Remind me to check my progress in 7 days"
```

---

## ❓ Common Questions

### Q: Where is my data stored?
**A:** Locally in `data/lifeline.db` - nothing leaves your computer except to OpenAI.

### Q: Can I use this offline?
**A:** Not quite - you need OpenAI API access to chat with the agent. But once events are logged, you can browse them offline.

### Q: How do I access from other computers?
**A:** The server runs on `0.0.0.0:8000`. Find your machine's IP and use:
```
http://<your-machine-ip>:8000
```

### Q: Can I customize the colors?
**A:** Yes! Edit `web/static/style.css` and change the CSS variables at the top.

### Q: What if something breaks?
**A:** See "Troubleshooting" section in `WEB_UI_README.md`.

---

## 🔧 Useful Commands

```bash
# Start the web server
make web

# Stop the server
Ctrl+C

# Run with different port
uvicorn web:app --port 8001

# Reset all data (WARNING: deletes everything!)
rm data/*.db

# Check code quality
make quality

# Run tests
make test

# View server logs
# Just look at the terminal output from 'make web'
```

---

## 📁 Project Structure

```
LifeLine/
├── web.py                    ← Backend server
├── web/
│   ├── index.html           ← Main page
│   └── static/
│       ├── style.css        ← Styling
│       └── app.js           ← Logic
├── lifeline/
│   ├── agent.py             ← AI agent
│   ├── database.py          ← Data storage
│   ├── tools.py             ← Agent functions
│   └── models.py            ← Data models
└── data/
    ├── lifeline.db          ← Your memories
    └── lifeline_web_user.db ← Chat history
```

---

## ✨ Features Overview

### Chat Interface
- Natural language conversation
- Real-time responses
- Message history
- Markdown formatting

### Timeline View
- Chronological events
- Category filtering
- Event details
- Beautiful design

### Statistics
- Total count
- Date range
- Category breakdown
- Visual charts

### Design
- Clean and modern
- Responsive (mobile-friendly)
- Dark/light ready
- Professional colors

---

## 🌐 Browser Support

Works great on:
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers

---

## 🚀 Ready?

### To start now:
```bash
make web
```

Then open: **http://localhost:8000**

### For more details:
Read: `QUICKSTART_WEB.md`

### For advanced topics:
Read: `WEB_UI_README.md`

---

## 📞 Need Help?

1. **Quick questions?** → `QUICKSTART_WEB.md`
2. **Technical issues?** → `WEB_UI_README.md` (Troubleshooting section)
3. **Want to understand the design?** → `WEB_UI_FEATURES.md`
4. **Curious about architecture?** → `WEB_UI_SUMMARY.md`

---

## 🎓 Learn as You Go

The interface is self-explanatory:
- **Sidebar** shows navigation and tips
- **Messages** are formatted like a chat app
- **Timeline** displays events beautifully
- **Statistics** show insights about your data

Just start using it and explore!

---

## 🎉 Summary

✅ **Install**: `uv sync`
✅ **Run**: `make web`
✅ **Open**: `http://localhost:8000`
✅ **Start logging**: Chat with LifeLine

Your personal memory assistant is ready to help you preserve life's meaningful moments!

---

**Everything set? Go to http://localhost:8000 and start logging your memories!**
