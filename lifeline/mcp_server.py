"""
MCP (Model Context Protocol) integration for LifeLine timeline data.

This module shows how to integrate LifeLine with MCP servers for external tools.
The OpenAI Agents SDK has built-in MCP support via agents.mcp module.

Example use cases:
- Expose timeline data to external MCP-compatible tools
- Connect LifeLine to filesystem servers, Git servers, etc.
- Build custom MCP servers that work with timeline data

Note: This is a simplified example showing the concept.
For production use, you'd create a proper MCP server following the
Model Context Protocol specification.
"""

from typing import Any
from pathlib import Path

from .database import TimelineDatabase
from .models import EventQuery


# Example: Using LifeLine with MCP servers (filesystem, git, etc.)
EXAMPLE_MCP_INTEGRATION = """
# Example: Using LifeLine agent with MCP servers
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from lifeline.agent import create_lifeline_agent

async def lifeline_with_mcp():
    # Connect to an MCP filesystem server
    samples_dir = Path("/path/to/documents")

    async with MCPServerStdio(
        name="Filesystem Server",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(samples_dir)]
        }
    ) as server:
        # Create LifeLine agent with MCP server access
        agent = create_lifeline_agent("data/lifeline.db")
        agent.mcp_servers = [server]

        # Now the agent can read files AND manage timeline
        result = await Runner.run(
            agent,
            "Read my journal.txt and log important events to my timeline"
        )
        print(result.final_output)
"""


class TimelineDataExporter:
    """Helper class to export timeline data for external tools."""

    def __init__(self, db_path: str = "data/lifeline.db"):
        """
        Initialize data exporter.

        Args:
            db_path: Path to LifeLine SQLite database
        """
        self.db = TimelineDatabase(db_path)

    def get_all_events(self) -> list[dict[str, Any]]:
        """Get all timeline events as JSON-serializable dicts."""
        query = EventQuery(limit=1000)
        events = self.db.query_events(query)
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

    def get_category_stats(self) -> list[dict[str, Any]]:
        """Get category statistics."""
        stats = self.db.get_category_stats()
        return [
            {
                "category": stat.category,
                "count": stat.count,
                "earliest_event": stat.earliest_event,
                "latest_event": stat.latest_event,
            }
            for stat in stats
        ]

    def get_timeline_stats(self) -> dict[str, Any]:
        """Get overall timeline statistics."""
        total = self.db.get_event_count()
        categories = self.db.get_category_stats()
        date_range = self.db.get_date_range()

        return {
            "total_events": total,
            "categories": {stat.category: stat.count for stat in categories},
            "date_range": {
                "earliest": date_range[0] if date_range else None,
                "latest": date_range[1] if date_range else None,
            },
        }

    def export_to_json(self, output_path: str):
        """Export all timeline data to a JSON file."""
        import json

        data = {
            "events": self.get_all_events(),
            "stats": self.get_timeline_stats(),
            "categories": self.get_category_stats(),
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)


def create_data_exporter(db_path: str = "data/lifeline.db") -> TimelineDataExporter:
    """
    Create a timeline data exporter.

    Args:
        db_path: Path to LifeLine database

    Returns:
        Configured TimelineDataExporter instance
    """
    return TimelineDataExporter(db_path)


# Example usage
if __name__ == "__main__":
    """
    Export LifeLine timeline data to JSON.

    Usage:
        python -m lifeline.mcp_server [db_path] [output.json]

    This exports all timeline data to a JSON file that can be consumed
    by external tools and visualization dashboards.
    """
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/lifeline.db"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/timeline_export.json"

    print(f"Exporting timeline data from: {db_path}")
    exporter = create_data_exporter(db_path)
    exporter.export_to_json(output_path)
    print(f"Timeline data exported to: {output_path}")
    print(f"Total events: {exporter.get_timeline_stats()['total_events']}")

    print("\nTo use LifeLine with MCP servers, see the example code in this file.")
    print("The OpenAI Agents SDK includes MCP support via agents.mcp module.")
