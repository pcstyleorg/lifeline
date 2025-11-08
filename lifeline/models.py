"""
Pydantic models for LifeLine timeline events and queries.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TimelineEvent(BaseModel):
    """A single event in the user's personal timeline."""

    id: Optional[int] = None
    title: str = Field(..., description="Brief title of the event")
    description: Optional[str] = Field(None, description="Detailed description of the event")
    category: str = Field(
        default="personal",
        description="Event category: career, travel, health, personal, learning, social, milestone, etc."
    )
    timestamp: str = Field(..., description="Event timestamp in ISO format")
    tags: list[str] = Field(default_factory=list, description="List of tags for categorization")
    created_at: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Normalize category to lowercase."""
        return v.lower().strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Normalize tags to lowercase and remove duplicates."""
        return list(set(tag.lower().strip() for tag in v))

    def __str__(self) -> str:
        """Human-readable string representation."""
        date_str = self.timestamp[:10]  # Extract date portion
        return f"[{self.category}] {self.title} - {date_str}"


class EventQuery(BaseModel):
    """Query parameters for searching timeline events."""

    search_text: Optional[str] = Field(None, description="Search in title and description")
    category: Optional[str] = Field(None, description="Filter by category")
    start_date: Optional[str] = Field(None, description="Start of date range (ISO format)")
    end_date: Optional[str] = Field(None, description="End of date range (ISO format)")
    tags: Optional[list[str]] = Field(None, description="Filter by tags (matches any)")
    limit: int = Field(default=50, description="Maximum number of results")


class EventSummary(BaseModel):
    """Summary of timeline events for agent responses."""

    total_events: int
    categories: dict[str, int] = Field(description="Count of events per category")
    date_range: Optional[tuple[str, str]] = Field(None, description="Earliest and latest event dates")
    recent_events: list[TimelineEvent] = Field(default_factory=list)

    def __str__(self) -> str:
        """Human-readable summary."""
        summary_parts = [f"Total events: {self.total_events}"]
        if self.categories:
            cat_str = ", ".join(f"{cat}: {count}" for cat, count in self.categories.items())
            summary_parts.append(f"Categories: {cat_str}")
        if self.date_range:
            summary_parts.append(f"Date range: {self.date_range[0]} to {self.date_range[1]}")
        return " | ".join(summary_parts)


class CategoryStats(BaseModel):
    """Statistics about event categories."""

    category: str
    count: int
    earliest_event: Optional[str] = None
    latest_event: Optional[str] = None
