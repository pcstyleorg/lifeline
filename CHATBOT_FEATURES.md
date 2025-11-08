# LifeLine Web - Chatbot Features

## Overview

Added comprehensive chatbot features including multiple chat sessions, dark mode, user onboarding, and customization settings.

## New Features

### 🎨 Dark Mode
- **System Preference Detection**: Automatically matches your system theme
- **Manual Control**: Switch between Light, Dark, and System modes
- **Persistent**: Theme preference saved across sessions
- **Smooth Transitions**: All components support dark mode
- **OLED Optimized**: True black backgrounds in dark mode

### 💬 Multiple Chat Sessions
- **Session Management**: Create, switch between, and delete chat sessions
- **Smart Titles**: Auto-generated from first message
- **Message Counts**: See how many messages in each chat
- **Session Persistence**: All chat history saved in database
- **Quick Navigation**: Sidebar with all your conversations

### 👋 Onboarding Flow
- **First-Time Experience**: Welcome modal on first visit
- **Name Collection**: Personalize your experience
- **Theme Selection**: Choose your preferred theme upfront
- **One-Time**: Only shows once, can be skipped

### ⚙️ Settings Panel
- **Profile Management**: Update your name anytime
- **Theme Control**: Change theme preference
- **Model Info**: View current AI model and settings
- **About Section**: Version and account information

### 🎯 Enhanced UX
- **Collapsible Sidebar**: Mobile-friendly hamburger menu
- **Welcome Message**: Personalized with user's name
- **Loading States**: Smooth transitions and loading indicators
- **Error Handling**: Graceful error messages
- **Auto-scroll**: Messages always visible

## Technical Implementation

### Backend (Python)

#### New Database: `lifeline/web_database.py`

```python
class WebDatabase:
    # Tables:
    # - user_preferences (profile, theme, model settings)
    # - chat_sessions (title, timestamps, message count)
    # - chat_messages (role, content, timestamps)
```

**Key Methods:**
- `get_user_preferences()` - Load user settings
- `create_session()` - Start new chat
- `get_user_sessions()` - List all chats
- `add_message()` - Save chat message
- `delete_session()` - Remove chat

#### Updated `web.py` API

**New Endpoints:**

```bash
# User Preferences
GET    /api/preferences          # Get user preferences
POST   /api/preferences          # Update preferences
POST   /api/onboarding           # Complete first-time setup

# Chat Sessions
POST   /api/sessions             # Create new session
GET    /api/sessions             # List all sessions
GET    /api/sessions/{id}        # Get specific session
PUT    /api/sessions/{id}        # Update session title
DELETE /api/sessions/{id}        # Delete session
GET    /api/sessions/{id}/messages  # Get session messages
```

**WebSocket Updates:**
- Session-aware chat
- Per-session memory persistence
- Auto-generated session titles

### Frontend (Next.js + React)

#### Context: `app/context/AppContext.tsx`

Global state management for:
- User preferences
- Chat sessions
- Theme control
- Session switching

```typescript
interface AppContextType {
  preferences: UserPreferences | null;
  sessions: ChatSession[];
  currentSessionId: number | null;
  isDark: boolean;
  updatePreferences: (updates) => Promise<void>;
  completeOnboarding: (name, theme) => Promise<void>;
  createSession: () => Promise<number>;
  setCurrentSession: (id) => void;
  deleteSession: (id) => Promise<void>;
  setTheme: (theme) => void;
}
```

#### New Components

**OnboardingModal**
- Collects user name
- Theme selection (3 options)
- Only shown once
- Smooth animations

**Sidebar**
- Session list with icons
- New chat button
- Settings button
- User info display
- Delete with confirmation
- Mobile-responsive

**SettingsModal**
- Profile editing
- Theme switcher
- Model information
- About section
- Save/Cancel actions

#### Updated Components

All components now support dark mode:
- `ChatMessage` - Dark backgrounds
- `ChatInput` - Dark input fields
- `Header` - Dark header bar
- `ThinkingIndicator` - Dark animation

## Usage

### First Time Setup

1. **Open the web app** → Onboarding modal appears
2. **Enter your name** → Personalizes experience
3. **Choose theme** → Light, Dark, or System
4. **Click "Get Started"** → Ready to chat!

### Using Multiple Sessions

1. **Click "New Chat"** → Creates fresh conversation
2. **Switch sessions** → Click any session in sidebar
3. **Delete session** → Hover and click trash icon
4. **Auto-titles** → First message becomes session name

### Changing Settings

1. **Open sidebar** → Click menu icon (mobile) or visible (desktop)
2. **Click "Settings"** → Opens settings modal
3. **Edit preferences** → Name, theme, etc.
4. **Save changes** → Updates instantly

### Dark Mode

**System Mode (Default):**
- Follows your OS theme
- Auto-switches with system

**Manual Override:**
1. Open Settings
2. Choose Light ☀️, Dark 🌙, or System 💻
3. Changes apply immediately

## Database Schema

### user_preferences
```sql
user_id TEXT PRIMARY KEY
name TEXT
theme TEXT ('system', 'light', 'dark')
model TEXT (default: 'gpt-4o')
temperature REAL (default: 0.7)
max_tokens INTEGER (default: 1500)
onboarded BOOLEAN (default: 0)
created_at TEXT
updated_at TEXT
```

### chat_sessions
```sql
id INTEGER PRIMARY KEY
user_id TEXT
title TEXT
created_at TEXT
updated_at TEXT
```

### chat_messages
```sql
id INTEGER PRIMARY KEY
session_id INTEGER (FK)
role TEXT ('user', 'assistant', 'system')
content TEXT
timestamp TEXT
```

## API Examples

### Complete Onboarding
```bash
POST /api/onboarding
{
  "name": "John",
  "theme": "dark"
}
```

### Create Session
```bash
POST /api/sessions?title=New+Chat
```

### Update Theme
```bash
POST /api/preferences
{
  "theme": "dark"
}
```

### Delete Session
```bash
DELETE /api/sessions/123
```

## Mobile Experience

### Responsive Design
- ✅ Collapsible sidebar with overlay
- ✅ Touch-friendly buttons (48px min)
- ✅ Full-screen modals
- ✅ Adaptive layouts
- ✅ Swipe-friendly session list

### Performance
- Lazy loading for sessions
- Optimized re-renders
- Efficient state management
- Minimal API calls

## Development

### Run Backend
```bash
make web
# or: uv run uvicorn web:app --reload --port 8000
```

### Run Frontend
```bash
cd web-ui
npm run dev
```

### Database Location
- Main DB: `data/lifeline.db` (timeline events)
- Web DB: `data/lifeline_web.db` (sessions, preferences)
- Agent Sessions: `data/agent_session_{id}.db` (per-session memory)

## Future Enhancements

Potential additions:
- [ ] Export chat sessions to markdown/PDF
- [ ] Search across all sessions
- [ ] Session folders/tags
- [ ] Favorite messages
- [ ] Chat templates
- [ ] Voice input
- [ ] File attachments
- [ ] Share sessions
- [ ] Advanced search filters
- [ ] Session statistics dashboard

## Troubleshooting

### Onboarding shows every time
- Check `data/lifeline_web.db` exists
- Verify `onboarded` flag in database
- Clear browser cache

### Dark mode not working
- Check browser DevTools for errors
- Verify `html` tag has `dark` class
- Check Tailwind CSS is loading

### Sessions not saving
- Verify backend is running
- Check network tab for API errors
- Ensure `data/` directory is writable

### Sidebar won't open (mobile)
- Check screen width < 1024px
- Verify hamburger button visible
- Check for JavaScript errors

## Technical Notes

- **State Management**: React Context + Hooks
- **Database**: SQLite with proper indexes
- **Theme System**: Tailwind `dark:` classes
- **Session Memory**: Separate SQLiteSession per chat
- **Auto-titles**: First 6 words of first message
- **Persistence**: All preferences saved to DB

## Summary

Built a complete chatbot experience with:
- ✅ Multiple chat sessions
- ✅ Dark mode (system-aware)
- ✅ User onboarding
- ✅ Settings panel
- ✅ Mobile-responsive
- ✅ Persistent state
- ✅ Clean UX

Total additions:
- ~1,500 lines of code
- 5 new components
- 1 new database module
- 8 new API endpoints
- Full dark mode support
