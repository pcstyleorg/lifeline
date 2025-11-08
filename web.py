"""
LifeLine Web - FastAPI backend with WebSocket chat.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from agents import Runner, SQLiteSession
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from lifeline.agent import create_lifeline_agent
from lifeline.database import TimelineDatabase

# Initialize FastAPI app
app = FastAPI(title="LifeLine Web API", version="0.1.0")

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

# Configuration
DB_PATH = "data/lifeline.db"
WEB_SESSION_ID = "lifeline_web_user"

# Ensure data directory exists
Path("data").mkdir(exist_ok=True)

# Initialize database
db = TimelineDatabase(DB_PATH)


# Request/Response models
class ChatMessage(BaseModel):
    message: str
    model: str = "gpt-4o"


class ChatResponse(BaseModel):
    response: str
    timestamp: str


# REST API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "LifeLine Web API", "version": "0.1.0"}


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
    - Client sends: {"message": "user message", "model": "gpt-4o"}
    - Server sends: {"type": "thinking"} when agent starts processing
    - Server sends: {"type": "message", "content": "...", "timestamp": "..."} for responses
    - Server sends: {"type": "error", "error": "..."} on errors
    """
    await websocket.accept()

    # Create agent and session
    model = "gpt-4o"
    agent = create_lifeline_agent(DB_PATH, model=model)
    session = SQLiteSession(WEB_SESSION_ID, f"data/{WEB_SESSION_ID}.db")

    try:
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

            # Update model if specified
            new_model = message_data.get("model")
            if new_model and new_model != model:
                model = new_model
                agent = create_lifeline_agent(DB_PATH, model=model)

            # Send thinking indicator
            await websocket.send_json({"type": "thinking"})

            try:
                # Run agent
                result = await Runner.run(
                    agent,
                    user_message,
                    session=session,
                    max_turns=10,
                )

                # Send response
                await websocket.send_json(
                    {
                        "type": "message",
                        "content": result.final_output,
                        "timestamp": datetime.now().isoformat(),
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
