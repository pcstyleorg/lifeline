"""
Example usage of LifeLine as a Python module.

This demonstrates how to use LifeLine programmatically
in your own Python applications.
"""

import asyncio
from agents import Runner, SQLiteSession
from lifeline.agent import create_lifeline_agent
from lifeline.database import TimelineDatabase


async def example_basic_usage():
    """Basic example: log events and query them."""
    print("=== Basic Usage Example ===\n")

    # Create agent with custom database path
    agent = create_lifeline_agent("data/example_timeline.db")

    # Create session for conversation memory
    session = SQLiteSession("example_user", "data/example_conversations.db")

    # Log some events
    print("1. Logging an event...")
    result = await Runner.run(
        agent,
        "Log: Had a great meeting with the product team about the new feature launch. "
        "It's a career milestone!",
        session=session,
    )
    print(f"Response: {result.final_output}\n")

    # Log another event with relative date
    print("2. Logging yesterday's event...")
    result = await Runner.run(
        agent,
        "Log: Yesterday I went hiking at Mount Tamalpais. The views were amazing! "
        "Category: travel",
        session=session,
    )
    print(f"Response: {result.final_output}\n")

    # Query recent events
    print("3. Getting recent events...")
    result = await Runner.run(
        agent,
        "What are my recent events?",
        session=session,
    )
    print(f"Response: {result.final_output}\n")


async def example_direct_database_access():
    """Example: Direct database access for custom queries."""
    print("\n=== Direct Database Access Example ===\n")

    # Access database directly
    db = TimelineDatabase("data/example_timeline.db")

    # Get statistics
    print("Timeline Statistics:")
    total = db.get_event_count()
    print(f"Total events: {total}")

    categories = db.get_all_categories()
    print(f"Categories: {', '.join(categories)}")

    # Get category stats
    stats = db.get_category_stats()
    for stat in stats:
        print(f"  - {stat.category}: {stat.count} events")

    # Get recent events
    print("\nRecent events:")
    recent = db.get_recent_events(limit=5)
    for event in recent:
        print(f"  - [{event.category}] {event.title} ({event.timestamp[:10]})")


async def example_multi_turn_conversation():
    """Example: Multi-turn conversation with context."""
    print("\n=== Multi-turn Conversation Example ===\n")

    agent = create_lifeline_agent("data/example_timeline.db")
    session = SQLiteSession("example_user", "data/example_conversations.db")

    # First turn: Log event
    print("Turn 1: Log an event")
    result = await Runner.run(
        agent,
        "Log: Started learning Python for data analysis",
        session=session,
    )
    print(f"Agent: {result.final_output}\n")

    # Second turn: Agent remembers context
    print("Turn 2: Follow-up question")
    result = await Runner.run(
        agent,
        "Add more details: I'm using Pandas and Jupyter notebooks",
        session=session,
    )
    print(f"Agent: {result.final_output}\n")

    # Third turn: Query related events
    print("Turn 3: Query learning events")
    result = await Runner.run(
        agent,
        "Show me all my learning category events",
        session=session,
    )
    print(f"Agent: {result.final_output}\n")


async def example_programmatic_logging():
    """Example: Programmatic event logging without agent."""
    print("\n=== Programmatic Logging Example ===\n")

    from lifeline.models import TimelineEvent
    from datetime import datetime

    db = TimelineDatabase("data/example_timeline.db")

    # Create events programmatically
    events = [
        TimelineEvent(
            title="Completed Machine Learning course",
            description="Finished Andrew Ng's ML course on Coursera",
            category="learning",
            timestamp="2025-01-10T18:00:00",
            tags=["coursera", "machine-learning", "certificate"],
        ),
        TimelineEvent(
            title="Team lunch celebration",
            description="Celebrated Q4 success with the team at the Italian restaurant",
            category="social",
            timestamp="2025-01-12T12:30:00",
            tags=["team", "celebration", "restaurant"],
        ),
        TimelineEvent(
            title="Hit 10K steps goal",
            description="Maintained daily walking streak for 30 days",
            category="health",
            timestamp="2025-01-14T20:00:00",
            tags=["fitness", "milestone", "walking"],
        ),
    ]

    for event in events:
        event_id = db.insert_event(event)
        print(f"Logged: {event.title} [ID: {event_id}]")


async def example_search_and_filter():
    """Example: Advanced search and filtering."""
    print("\n=== Search and Filter Example ===\n")

    agent = create_lifeline_agent("data/example_timeline.db")
    session = SQLiteSession("example_user", "data/example_conversations.db")

    # Search by text
    print("1. Search for 'learning' events:")
    result = await Runner.run(
        agent,
        "Search for events related to learning or courses",
        session=session,
    )
    print(f"Response: {result.final_output}\n")

    # Filter by date range
    print("2. Events from January 2025:")
    result = await Runner.run(
        agent,
        "Show me all events from January 2025",
        session=session,
    )
    print(f"Response: {result.final_output}\n")

    # Filter by category
    print("3. All health-related events:")
    result = await Runner.run(
        agent,
        "What are my health and fitness memories?",
        session=session,
    )
    print(f"Response: {result.final_output}\n")


async def example_reminder_system():
    """Example: Using the reminder system."""
    print("\n=== Reminder System Example ===\n")

    agent = create_lifeline_agent("data/example_timeline.db")
    session = SQLiteSession("example_user", "data/example_conversations.db")

    # Set a reminder
    print("1. Setting a reminder for 10 days from now:")
    result = await Runner.run(
        agent,
        "Remind me to cancel my Netflix subscription in 10 days",
        session=session,
    )
    print(f"Agent: {result.final_output}\n")

    # Set another reminder
    print("2. Setting a reminder for tomorrow:")
    result = await Runner.run(
        agent,
        "Remind me tomorrow to call the dentist",
        session=session,
    )
    print(f"Agent: {result.final_output}\n")

    # View upcoming reminders
    print("3. Viewing upcoming reminders:")
    result = await Runner.run(
        agent,
        "What are my upcoming reminders?",
        session=session,
    )
    print(f"Agent: {result.final_output}\n")

    # The agent properly uses date tools
    print("4. Testing date awareness - asking what day it is:")
    result = await Runner.run(
        agent,
        "What day is today?",
        session=session,
    )
    print(f"Agent: {result.final_output}\n")


async def main():
    """Run all examples."""
    try:
        await example_basic_usage()
        await example_direct_database_access()
        await example_multi_turn_conversation()
        await example_programmatic_logging()
        await example_search_and_filter()
        await example_reminder_system()

        print("\n=== Examples Complete ===")
        print("Check data/example_timeline.db for the logged events")
        print("Check data/example_conversations.db for conversation history")
        print("\nNew features demonstrated:")
        print("  - Reminder system with proper date calculations")
        print("  - Date awareness (agent knows today's date)")
        print("  - Future date calculations")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    # Make sure OPENAI_API_KEY is set in your environment
    import os

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        exit(1)

    print("Running LifeLine examples...\n")
    asyncio.run(main())
