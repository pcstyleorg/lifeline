"""
SQLite database operations for LifeLine timeline events.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

from .models import TimelineEvent, EventQuery, CategoryStats


class TimelineDatabase:
    """Manages SQLite database for timeline events."""

    def __init__(self, db_path: str = "data/lifeline.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database()

    def _ensure_database(self):
        """Create database and tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'personal',
                    timestamp TEXT NOT NULL,
                    tags TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON events(category)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)
            """)
            conn.commit()

    def insert_event(self, event: TimelineEvent) -> int:
        """
        Insert a new timeline event.

        Args:
            event: TimelineEvent to insert

        Returns:
            ID of the inserted event
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO events (title, description, category, timestamp, tags)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event.title,
                    event.description,
                    event.category,
                    event.timestamp,
                    json.dumps(event.tags) if event.tags else None,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def query_events(self, query: EventQuery) -> list[TimelineEvent]:
        """
        Query events with various filters.

        Args:
            query: EventQuery with filter parameters

        Returns:
            List of matching TimelineEvent objects
        """
        sql = "SELECT id, title, description, category, timestamp, tags, created_at FROM events WHERE 1=1"
        params = []

        # Add filters
        if query.category:
            sql += " AND category = ?"
            params.append(query.category.lower())

        if query.start_date:
            sql += " AND timestamp >= ?"
            params.append(query.start_date)

        if query.end_date:
            sql += " AND timestamp <= ?"
            params.append(query.end_date)

        if query.search_text:
            sql += " AND (title LIKE ? OR description LIKE ?)"
            search_pattern = f"%{query.search_text}%"
            params.extend([search_pattern, search_pattern])

        # Order by timestamp descending
        sql += " ORDER BY timestamp DESC"

        if query.limit:
            sql += " LIMIT ?"
            params.append(query.limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            events = []
            for row in cursor.fetchall():
                tags = json.loads(row["tags"]) if row["tags"] else []

                # Apply tag filter if specified
                if query.tags and not any(tag in tags for tag in query.tags):
                    continue

                events.append(
                    TimelineEvent(
                        id=row["id"],
                        title=row["title"],
                        description=row["description"],
                        category=row["category"],
                        timestamp=row["timestamp"],
                        tags=tags,
                        created_at=row["created_at"],
                    )
                )
            return events

    def get_recent_events(self, limit: int = 10) -> list[TimelineEvent]:
        """Get the most recent events."""
        query = EventQuery(limit=limit)
        return self.query_events(query)

    def get_all_categories(self) -> list[str]:
        """Get list of all unique categories."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT category FROM events ORDER BY category")
            return [row[0] for row in cursor.fetchall()]

    def get_category_stats(self) -> list[CategoryStats]:
        """Get statistics for each category."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT
                    category,
                    COUNT(*) as count,
                    MIN(timestamp) as earliest,
                    MAX(timestamp) as latest
                FROM events
                GROUP BY category
                ORDER BY count DESC
            """)
            stats = []
            for row in cursor.fetchall():
                stats.append(
                    CategoryStats(
                        category=row["category"],
                        count=row["count"],
                        earliest_event=row["earliest"],
                        latest_event=row["latest"],
                    )
                )
            return stats

    def get_event_count(self) -> int:
        """Get total number of events."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM events")
            return cursor.fetchone()[0]

    def delete_event(self, event_id: int) -> bool:
        """
        Delete an event by ID.

        Args:
            event_id: ID of event to delete

        Returns:
            True if event was deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_date_range(self) -> Optional[tuple[str, str]]:
        """Get the earliest and latest event timestamps."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT MIN(timestamp), MAX(timestamp) FROM events")
            result = cursor.fetchone()
            if result[0] and result[1]:
                return (result[0], result[1])
            return None
