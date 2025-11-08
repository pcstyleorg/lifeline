"""
LifeLine Web - FastAPI backend with WebSocket chat and session management.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from agents import Runner, SQLiteSession
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from lifeline.agent import create_lifeline_agent
from lifeline.api_key import ensure_api_key
from lifeline.database import TimelineDatabase
from lifeline.web_database import WebDatabase, UserPreferences, ChatSession

# Initialize FastAPI app
app = FastAPI(title="LifeLine Web API", version="0.2.0")

# CORS middleware for Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - detect if running from app bundle
def get_data_dir():
    """Get data directory - use ~/.lifeline if running from app bundle, else ./data"""
    # simplest check: if cwd is in Contents/Resources, we're in app bundle
    try:
        cwd = Path.cwd().resolve()
        # check if current directory path contains Contents/Resources
        if 'Contents' in cwd.parts and 'Resources' in cwd.parts:
            data_dir = Path.home() / ".lifeline"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir
    except Exception:
        pass
    
    # also check executable path (for PyInstaller bundles)
    try:
        if sys.executable:
            exe_path = Path(sys.executable).resolve()
            if 'Contents' in exe_path.parts and 'Resources' in exe_path.parts:
                data_dir = Path.home() / ".lifeline"
                data_dir.mkdir(parents=True, exist_ok=True)
                return data_dir
    except Exception:
        pass
    
    # default to local data directory
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

DATA_DIR = get_data_dir()
DB_PATH = str(DATA_DIR / "lifeline.db")
WEB_DB_PATH = str(DATA_DIR / "lifeline_web.db")

# Initialize databases
db = TimelineDatabase(DB_PATH)
web_db = WebDatabase(WEB_DB_PATH)


@app.on_event("startup")
def startup_event():
    """Ensure API key is available on startup."""
    try:
        ensure_api_key()
    except SystemExit:
        # allow server to start without API key (will prompt on first use)
        print("Warning: No API key found. Server will start but chat will require API key setup.")


# Request/Response models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[int] = None
    model: str = "gpt-4o"


class ChatResponse(BaseModel):
    response: str
    timestamp: str


class OnboardingData(BaseModel):
    name: str
    theme: str = "system"


class PreferencesUpdate(BaseModel):
    name: Optional[str] = None
    theme: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


# REST API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "LifeLine Web API", "version": "0.2.0"}


# User Preferences Endpoints
@app.get("/api/preferences")
async def get_preferences(user_id: str = "default_user"):
    """Get user preferences."""
    try:
        prefs = web_db.get_user_preferences(user_id)
        if not prefs:
            # Create default preferences
            prefs = UserPreferences(user_id=user_id)
            prefs = web_db.create_user_preferences(prefs)
        return prefs.model_dump()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/preferences")
async def update_preferences(
    prefs_update: PreferencesUpdate, user_id: str = "default_user"
):
    """Update user preferences."""
    try:
        updates = {k: v for k, v in prefs_update.model_dump().items() if v is not None}
        prefs = web_db.update_user_preferences(user_id, **updates)
        return prefs.model_dump() if prefs else {"error": "Failed to update"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/onboarding")
async def complete_onboarding(data: OnboardingData, user_id: str = "default_user"):
    """Complete user onboarding."""
    try:
        prefs = web_db.update_user_preferences(
            user_id, name=data.name, theme=data.theme, onboarded=True
        )
        return prefs.model_dump() if prefs else {"error": "Failed to onboard"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Chat Session Endpoints
@app.post("/api/sessions")
async def create_session(user_id: str = "default_user", title: str = "New Chat"):
    """Create a new chat session."""
    try:
        session_id = web_db.create_session(user_id, title)
        session = web_db.get_session(session_id)
        return session.model_dump() if session else {"error": "Failed to create session"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/sessions")
async def get_sessions(user_id: str = "default_user", limit: int = 50):
    """Get all chat sessions for a user."""
    try:
        sessions = web_db.get_user_sessions(user_id, limit)
        return [s.model_dump() for s in sessions]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: int):
    """Get a specific chat session."""
    try:
        session = web_db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.put("/api/sessions/{session_id}")
async def update_session(session_id: int, title: str):
    """Update session title."""
    try:
        success = web_db.update_session_title(session_id, title)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": "Session updated"}
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: int):
    """Delete a chat session."""
    try:
        success = web_db.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": "Session deleted"}
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: int, limit: Optional[int] = None):
    """Get messages for a session."""
    try:
        messages = web_db.get_session_messages(session_id, limit)
        return [m.model_dump() for m in messages]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Timeline Stats Endpoints
@app.get("/api/stats")
async def get_stats():
    """Get timeline statistics."""
    try:
        total = db.get_event_count()
        stats = db.get_category_stats()
        date_range = db.get_date_range()

        return JSONResponse(
            {
                "total_events": total,
                "categories": [
                    {
                        "category": stat.category,
                        "count": stat.count,
                        "earliest": stat.earliest_event,
                        "latest": stat.latest_event,
                    }
                    for stat in stats
                ],
                "date_range": {
                    "start": date_range[0] if date_range else None,
                    "end": date_range[1] if date_range else None,
                },
            }
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/events/recent")
async def get_recent_events(limit: int = 10):
    """Get recent events."""
    try:
        events = db.get_recent_events(limit=limit)
        return JSONResponse(
            {
                "events": [
                    {
                        "id": event.id,
                        "title": event.title,
                        "description": event.description,
                        "category": event.category,
                        "timestamp": event.timestamp,
                        "tags": event.tags,
                        "created_at": event.created_at,
                    }
                    for event in events
                ]
            }
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/categories")
async def get_categories():
    """Get all categories."""
    try:
        categories = db.get_all_categories()
        return JSONResponse({"categories": categories})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cleardb")
async def clear_database():
    """Clear all timeline data (DANGEROUS - requires confirmation)."""
    try:
        deleted_count = db.clear_all_events()
        return JSONResponse(
            {"success": True, "deleted_count": deleted_count, "message": "Database cleared"}
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# WebSocket Chat Endpoint
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat with LifeLine agent.

    Protocol:
    - Client sends: {"message": "user message", "session_id": 1, "model": "gpt-4o"}
    - Server sends: {"type": "thinking"} when agent starts processing
    - Server sends: {"type": "message", "content": "...", "timestamp": "..."} for responses
    - Server sends: {"type": "error", "error": "..."} on errors
    """
    await websocket.accept()

    # Default configuration
    user_id = "default_user"
    current_session_id = None
    model = "gpt-4o"
    agent = create_lifeline_agent(DB_PATH, model=model)

    try:
        # Get or create user preferences
        prefs = web_db.get_user_preferences(user_id)
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            web_db.create_user_preferences(prefs)

        # Send welcome message
        await websocket.send_json(
            {
                "type": "message",
                "content": "Welcome to LifeLine! I'm here to help you capture and organize your life's meaningful moments. How can I help you today?",
                "timestamp": datetime.now().isoformat(),
            }
        )

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            user_message = message_data.get("message", "").strip()
            if not user_message:
                continue

            # Get or create session
            session_id = message_data.get("session_id")
            if session_id:
                current_session_id = session_id
            elif not current_session_id:
                # Create new session with smart title
                current_session_id = web_db.create_session(user_id, "New Chat")

            # Update model if specified
            new_model = message_data.get("model")
            if new_model and new_model != model:
                model = new_model
                agent = create_lifeline_agent(DB_PATH, model=model)

            # Save user message
            web_db.add_message(current_session_id, "user", user_message)

            # Send thinking indicator
            await websocket.send_json({"type": "thinking"})

            try:
                # Create session for agent (reuse across messages in same session)
                agent_session = SQLiteSession(
                    f"web_session_{current_session_id}", f"data/agent_session_{current_session_id}.db"
                )

                # Run agent
                result = await Runner.run(
                    agent,
                    user_message,
                    session=agent_session,
                    max_turns=10,
                )

                response_content = result.final_output

                # Save assistant message
                web_db.add_message(current_session_id, "assistant", response_content)

                # Auto-generate session title from first message if still "New Chat"
                session = web_db.get_session(current_session_id)
                if session and session.title == "New Chat" and session.message_count <= 2:
                    # Use first few words of user message as title
                    title_words = user_message.split()[:6]
                    new_title = " ".join(title_words)
                    if len(user_message.split()) > 6:
                        new_title += "..."
                    web_db.update_session_title(current_session_id, new_title)

                # Send response
                await websocket.send_json(
                    {
                        "type": "message",
                        "content": response_content,
                        "timestamp": datetime.now().isoformat(),
                        "session_id": current_session_id,
                    }
                )

            except Exception as e:
                # Send error
                await websocket.send_json({"type": "error", "error": str(e)})

    except WebSocketDisconnect:
        print(f"Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "error": str(e)})
        except Exception:
            pass


# Run with: uvicorn web:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
