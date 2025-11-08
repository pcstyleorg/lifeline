"""
Function tools for LifeLine agent timeline operations.
"""

from datetime import datetime, timedelta
from typing import Annotated, Any
from agents import function_tool

from .database import TimelineDatabase
from .models import TimelineEvent, EventQuery

# Optional web search support
try:
    import os
    WEB_SEARCH_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except:
    WEB_SEARCH_AVAILABLE = False


# Global database instance (initialized by agent)
_db: TimelineDatabase = None


def init_tools(db_path: str = "data/lifeline.db"):
    """Initialize the database for tools."""
    global _db
    _db = TimelineDatabase(db_path)


@function_tool
def get_current_datetime() -> str:
    """
    IMPORTANT: Use this tool FIRST when the user mentions any time-related requests like 'today', 'tomorrow', 'in X days', etc.
    Get the current date and time.

    Returns:
        Current datetime as ISO string with human-readable format, e.g., "2025-11-08T14:30:00 (Friday, November 8, 2025 at 2:30 PM)"
    """
    now = datetime.now()
    iso_str = now.isoformat()
    readable = now.strftime("%A, %B %d, %Y at %I:%M %p")
    return f"{iso_str} ({readable})"


@function_tool
def get_todays_date() -> str:
    """
    Get today's date in a clear format. Use this when you need to know what day it is RIGHT NOW.

    Returns:
        Today's date with day of week, e.g., "2025-11-08 (Friday, November 8, 2025)"
    """
    today = datetime.now()
    iso_date = today.strftime("%Y-%m-%d")
    readable = today.strftime("%A, %B %d, %Y")
    return f"{iso_date} ({readable})"


@function_tool
def calculate_future_date(days_from_now: Annotated[int, "Number of days from today"]) -> str:
    """
    Calculate a future date by adding days to today's date.
    Use this for reminders like "remind me in 10 days".

    Args:
        days_from_now: Number of days to add to today

    Returns:
        Future date with day of week, e.g., "2025-11-18 (Monday, November 18, 2025)"
    """
    today = datetime.now()
    future_date = today + timedelta(days=days_from_now)
    iso_date = future_date.strftime("%Y-%m-%d")
    readable = future_date.strftime("%A, %B %d, %Y")
    return f"{iso_date} ({readable})"


@function_tool
def parse_relative_date(
    relative_term: Annotated[str, "Relative date like 'today', 'yesterday', 'last week', 'two days ago'"]
) -> str:
    """
    Convert relative date terms to ISO format timestamps.

    Args:
        relative_term: Natural language relative date

    Returns:
        ISO format date string
    """
    now = datetime.now()
    term = relative_term.lower().strip()

    if term == "today":
        return now.date().isoformat()
    elif term == "yesterday":
        return (now - timedelta(days=1)).date().isoformat()
    elif term == "tomorrow":
        return (now + timedelta(days=1)).date().isoformat()
    elif "last week" in term:
        return (now - timedelta(weeks=1)).date().isoformat()
    elif "last month" in term:
        return (now - timedelta(days=30)).date().isoformat()
    elif "days ago" in term:
        # Extract number of days
        try:
            days = int(''.join(filter(str.isdigit, term)))
            return (now - timedelta(days=days)).date().isoformat()
        except ValueError:
            return now.date().isoformat()
    elif "weeks ago" in term:
        try:
            weeks = int(''.join(filter(str.isdigit, term)))
            return (now - timedelta(weeks=weeks)).date().isoformat()
        except ValueError:
            return now.date().isoformat()
    else:
        # Default to today
        return now.date().isoformat()


@function_tool
def log_event(
    title: Annotated[str, "Brief title of the event"],
    description: Annotated[str, "Detailed description of what happened"],
    category: Annotated[str, "Category: career, travel, health, personal, learning, social, milestone, etc."] = "personal",
    timestamp: Annotated[str, "ISO format timestamp (use get_current_datetime or parse_relative_date)"] = None,
    tags: Annotated[list[str], "Optional tags for the event"] = None,
) -> str:
    """
    Log a new event to the user's personal timeline.

    Args:
        title: Brief title summarizing the event
        description: Detailed description of the event
        category: Event category for organization
        timestamp: When the event occurred (ISO format)
        tags: Optional list of tags

    Returns:
        Confirmation message with event ID
    """
    if _db is None:
        return "Error: Database not initialized"

    # Use current time if not provided
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    event = TimelineEvent(
        title=title,
        description=description,
        category=category.lower(),
        timestamp=timestamp,
        tags=tags or [],
    )

    try:
        event_id = _db.insert_event(event)
        return f"Event logged successfully! [ID: {event_id}] '{title}' added to {category} category at {timestamp[:16]}"
    except Exception as e:
        return f"Error logging event: {str(e)}"


@function_tool
def query_events_by_date(
    start_date: Annotated[str, "Start date in ISO format (YYYY-MM-DD)"] = None,
    end_date: Annotated[str, "End date in ISO format (YYYY-MM-DD)"] = None,
    limit: Annotated[int, "Maximum number of events to return"] = 50,
) -> list[dict]:
    """
    Query timeline events within a date range.

    Args:
        start_date: Beginning of date range (inclusive)
        end_date: End of date range (inclusive)
        limit: Maximum results to return

    Returns:
        List of events as dictionaries
    """
    if _db is None:
        return [{"error": "Database not initialized"}]

    query = EventQuery(start_date=start_date, end_date=end_date, limit=limit)
    events = _db.query_events(query)

    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "category": e.category,
            "timestamp": e.timestamp,
            "tags": e.tags,
        }
        for e in events
    ]


@function_tool
def query_events_by_category(
    category: Annotated[str, "Category to filter by (e.g., 'travel', 'career', 'health')"],
    limit: Annotated[int, "Maximum number of events to return"] = 50,
) -> list[dict]:
    """
    Retrieve all events from a specific category.

    Args:
        category: Category name to filter by
        limit: Maximum results

    Returns:
        List of events in the specified category
    """
    if _db is None:
        return [{"error": "Database not initialized"}]

    query = EventQuery(category=category, limit=limit)
    events = _db.query_events(query)

    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "category": e.category,
            "timestamp": e.timestamp,
            "tags": e.tags,
        }
        for e in events
    ]


@function_tool
def search_events(
    search_text: Annotated[str, "Text to search for in event titles and descriptions"],
    limit: Annotated[int, "Maximum number of results"] = 50,
) -> list[dict]:
    """
    Search events by text content.

    Args:
        search_text: Search query
        limit: Maximum results

    Returns:
        List of matching events
    """
    if _db is None:
        return [{"error": "Database not initialized"}]

    query = EventQuery(search_text=search_text, limit=limit)
    events = _db.query_events(query)

    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "category": e.category,
            "timestamp": e.timestamp,
            "tags": e.tags,
        }
        for e in events
    ]


@function_tool
def get_recent_events(limit: Annotated[int, "Number of recent events to retrieve"] = 10) -> list[dict]:
    """
    Get the most recent timeline events.

    Args:
        limit: Number of events to return

    Returns:
        List of recent events, newest first
    """
    if _db is None:
        return [{"error": "Database not initialized"}]

    events = _db.get_recent_events(limit=limit)

    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "category": e.category,
            "timestamp": e.timestamp,
            "tags": e.tags,
        }
        for e in events
    ]


@function_tool
def get_all_categories() -> list[str]:
    """
    Get a list of all categories currently in use.

    Returns:
        List of category names
    """
    if _db is None:
        return ["Error: Database not initialized"]

    return _db.get_all_categories()


@function_tool
def get_timeline_statistics() -> dict:
    """
    Get overall statistics about the user's timeline.

    Returns:
        Dictionary with stats including total events, categories, date range
    """
    if _db is None:
        return {"error": "Database not initialized"}

    total = _db.get_event_count()
    categories = _db.get_category_stats()
    date_range = _db.get_date_range()

    return {
        "total_events": total,
        "categories": {stat.category: stat.count for stat in categories},
        "date_range": {
            "earliest": date_range[0] if date_range else None,
            "latest": date_range[1] if date_range else None,
        },
        "category_details": [
            {
                "category": stat.category,
                "count": stat.count,
                "earliest": stat.earliest_event,
                "latest": stat.latest_event,
            }
            for stat in categories
        ],
    }


@function_tool
def set_reminder(
    title: Annotated[str, "Brief title for the reminder"],
    description: Annotated[str, "What needs to be done"],
    due_date: Annotated[str, "ISO format date when reminder is due (YYYY-MM-DD). Use calculate_future_date tool first!"],
    tags: Annotated[list[str], "Optional tags"] = None,
) -> str:
    """
    Set a reminder for a future task or event.
    IMPORTANT: Always use calculate_future_date or get_todays_date FIRST to get the correct due date!

    Args:
        title: Brief reminder title
        description: Detailed description of what to do
        due_date: ISO format date (YYYY-MM-DD)
        tags: Optional tags like ['urgent', 'subscription', etc.]

    Returns:
        Confirmation message
    """
    if _db is None:
        return "Error: Database not initialized"

    # Create as a timeline event with 'reminder' category
    event = TimelineEvent(
        title=f"REMINDER: {title}",
        description=description,
        category="reminder",
        timestamp=f"{due_date}T09:00:00",  # Set to 9 AM on due date
        tags=tags or [],
    )

    try:
        event_id = _db.insert_event(event)
        return f"Reminder set! [ID: {event_id}] '{title}' due on {due_date}. I'll track this in your timeline."
    except Exception as e:
        return f"Error setting reminder: {str(e)}"


@function_tool
def get_upcoming_reminders(days_ahead: Annotated[int, "Number of days to look ahead"] = 30) -> list[dict]:
    """
    Get all upcoming reminders within the next X days.

    Args:
        days_ahead: Number of days to look ahead (default 30)

    Returns:
        List of upcoming reminders
    """
    if _db is None:
        return [{"error": "Database not initialized"}]

    today = datetime.now()
    end_date = today + timedelta(days=days_ahead)

    query = EventQuery(
        category="reminder",
        start_date=today.isoformat(),
        end_date=end_date.isoformat(),
        limit=100,
    )
    reminders = _db.query_events(query)

    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "due_date": r.timestamp[:10],  # Just the date part
            "tags": r.tags,
        }
        for r in reminders
    ]


@function_tool
def search_web(
    query: Annotated[str, "Search query to look up on the web"],
) -> str:
    """
    Search the web for current information.
    Use this when you need up-to-date information, facts, or current events.

    Args:
        query: What to search for

    Returns:
        Search results summary
    """
    # Note: This is a placeholder. In a real implementation with WebSearch tool available,
    # we'd integrate with the actual search functionality.
    # For now, we inform the user that web search would happen here.
    return (
        f"Web search for '{query}' would be performed here. "
        "To enable web search, integrate with the WebSearch tool in the agent runner. "
        "For now, I can help with timeline and reminder management based on information you provide."
    )


# List of all tools for agent initialization
ALL_TOOLS = [
    get_todays_date,
    get_current_datetime,
    calculate_future_date,
    parse_relative_date,
    log_event,
    set_reminder,
    get_upcoming_reminders,
    query_events_by_date,
    query_events_by_category,
    search_events,
    get_recent_events,
    get_all_categories,
    get_timeline_statistics,
    search_web,
]
