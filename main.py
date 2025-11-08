"""
LifeLine - Personal Memory & Timeline Assistant
CLI interface with autocomplete and enhanced UX.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from agents import Runner, SQLiteSession
from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from lifeline.agent import create_lifeline_agent
from lifeline.database import TimelineDatabase


# Rich console for beautiful output
console = Console()

# Cache for available models (fetched from API)
_available_models_cache: Optional[list[str]] = None


async def fetch_available_models() -> list[str]:
    """Fetch available models from OpenAI API."""
    global _available_models_cache

    # Return cached if available
    if _available_models_cache is not None:
        return _available_models_cache

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Fallback to common models if API key not set
        console.print("[yellow]Warning: OPENAI_API_KEY not set, using default models[/yellow]")
        _available_models_cache = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini",
        ]
        return _available_models_cache

    try:
        # Use OpenAI client to fetch models
        client = OpenAI(api_key=api_key)

        # Fetch models in a thread to avoid blocking
        def get_models():
            models = client.models.list()
            # Filter for chat/completion models (exclude embeddings, etc.)
            chat_models = []
            for model in models.data:
                model_id = model.id
                # Include common chat models and custom fine-tuned models
                if (
                    model_id.startswith("gpt-")
                    or model_id.startswith("o1-")
                    or model_id.startswith("ft:")
                    or "gpt" in model_id.lower()
                ):
                    chat_models.append(model_id)
            return sorted(chat_models)

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        models = await loop.run_in_executor(None, get_models)

        if models:
            _available_models_cache = models
            return models
        else:
            # Fallback if no models found
            console.print("[yellow]Warning: No models found, using defaults[/yellow]")
            _available_models_cache = [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
                "o1-preview",
                "o1-mini",
            ]
            return _available_models_cache

    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch models from API: {e}[/yellow]")
        console.print("[dim]Using default models. Custom models can still be used by name.[/dim]")
        # Fallback to defaults
        _available_models_cache = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini",
        ]
        return _available_models_cache

# Command definitions with aliases and descriptions
COMMANDS = {
    "/help": {"aliases": ["/h", "help"], "desc": "Show help message"},
    "/quit": {"aliases": ["/q", "/exit", "quit", "exit"], "desc": "Exit LifeLine"},
    "/stats": {"aliases": ["/s", "stats"], "desc": "Show timeline statistics"},
    "/clear": {"aliases": ["/c", "clear"], "desc": "Clear conversation history"},
    "/categories": {"aliases": ["/cat", "categories"], "desc": "List all categories"},
    "/recent": {"aliases": ["/r", "recent"], "desc": "Show recent events"},
    "/search": {"aliases": ["/find", "search"], "desc": "Search events (usage: /search <query>)"},
    "/model": {"aliases": ["/m", "model"], "desc": "Switch model (usage: /model <model_name>)"},
}


class CommandCompleter(Completer):
    """Autocomplete completer for LifeLine commands."""

    def __init__(self, db: Optional[TimelineDatabase] = None, available_models: Optional[list[str]] = None):
        self.db = db
        self.available_models = available_models or []
        # Build command list with aliases
        self.commands = []
        for cmd, info in COMMANDS.items():
            self.commands.append(cmd)
            self.commands.extend(info["aliases"])

    def get_completions(self, document, complete_event):
        """Provide command completions."""
        text = document.text_before_cursor.lower().strip()
        words = text.split()

        # If starts with /, complete commands
        if text.startswith("/") or not text:
            for cmd in sorted(set(self.commands)):
                if cmd.startswith(text) or (not text.startswith("/") and cmd.replace("/", "").startswith(text)):
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=cmd,
                        display_meta=COMMANDS.get(cmd, {}).get("desc", "Command"),
                    )

        # If /search, suggest categories
        if text.startswith("/search") or text.startswith("/find"):
            if self.db:
                try:
                    categories = self.db.get_all_categories()
                    query = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""
                    for cat in categories:
                        if query.lower() in cat.lower():
                            yield Completion(
                                f"/search {cat}",
                                start_position=-len(query),
                                display=f"Search in {cat}",
                            )
                except Exception:
                    pass

        # If /model, suggest available models
        if text.startswith("/model") or text.startswith("/m"):
            if len(words) == 1:
                # Just "/model" - suggest all models
                for model in self.available_models:
                    yield Completion(
                        f"/model {model}",
                        start_position=-len(text),
                        display=model,
                        display_meta="OpenAI model",
                    )
            elif len(words) == 2:
                # "/model <partial>" - suggest matching models
                partial = words[1].lower()
                for model in self.available_models:
                    if partial in model.lower():
                        yield Completion(
                            f"/model {model}",
                            start_position=-len(words[1]),
                            display=model,
                            display_meta="OpenAI model",
                        )


def print_welcome():
    """Display welcome message."""
    welcome_text = """
# LifeLine - Your Personal Memory & Timeline Assistant

Welcome! I'm here to help you capture, organize, and reflect on the meaningful moments of your life.

**What I can do:**
- Log life events, memories, and milestones
- Organize entries by category (career, travel, health, personal, learning, etc.)
- Retrieve past memories by date, category, or search
- Provide insights and reflections on your timeline

**Special commands:**
- `/help` or `/h` - Show this help message
- `/quit` or `/exit` - Exit LifeLine
- `/stats` or `/s` - Show timeline statistics
- `/clear` or `/c` - Clear conversation history (keeps timeline data)
- `/categories` or `/cat` - List all categories
- `/recent` or `/r` - Show recent events
- `/search <query>` or `/find <query>` - Search events
- `/model [name]` or `/m [name]` - Switch model or list available models

**Tips:**
- Press `Tab` to autocomplete commands
- Use `↑/↓` arrows for command history
- Type `/` and press `Tab` to see all commands

**Getting started:**
Just tell me what you want to log or ask about! For example:
- "Log: I started learning Python today"
- "What did I do last week?"
- "Show my travel memories"

Let's preserve your life's meaningful moments together!
"""
    console.print(Panel(Markdown(welcome_text), title="LifeLine", border_style="blue"))


def print_stats(db: TimelineDatabase):
    """Display timeline statistics."""
    stats = db.get_category_stats()
    total = db.get_event_count()
    date_range = db.get_date_range()

    stats_text = f"**Total Events:** {total}\n\n"

    if date_range:
        stats_text += f"**Timeline Range:** {date_range[0][:10]} to {date_range[1][:10]}\n\n"

    if stats:
        stats_text += "**Events by Category:**\n"
        for stat in stats:
            stats_text += f"- {stat.category}: {stat.count}\n"

    console.print(Panel(Markdown(stats_text), title="Timeline Statistics", border_style="green"))


def print_categories(db: TimelineDatabase):
    """Display all categories."""
    categories = db.get_all_categories()
    stats = db.get_category_stats()

    if not categories:
        console.print("[yellow]No categories found. Start logging events to create categories![/yellow]")
        return

    table = Table(title="Categories", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="green")

    # Create a dict for quick lookup
    stats_dict = {stat.category: stat.count for stat in stats}

    for cat in sorted(categories):
        count = stats_dict.get(cat, 0)
        table.add_row(cat, str(count))

    console.print(table)


def print_recent(db: TimelineDatabase, limit: int = 10):
    """Display recent events."""
    events = db.get_recent_events(limit=limit)

    if not events:
        console.print("[yellow]No events found. Start logging memories![/yellow]")
        return

    table = Table(title=f"Recent Events (last {limit})", show_header=True, header_style="bold magenta")
    table.add_column("Date", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Category", style="green", no_wrap=True)

    for event in events:
        date_str = event.timestamp[:10] if len(event.timestamp) >= 10 else event.timestamp
        table.add_row(date_str, event.title[:50], event.category)

    console.print(table)


def print_models(current_model: str, available_models: list[str]):
    """Display available models."""
    table = Table(title="Available Models", show_header=True, header_style="bold magenta")
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Status", style="green", no_wrap=True)

    for model in available_models:
        status = "✓ Current" if model == current_model else ""
        table.add_row(model, status)

    console.print(table)
    console.print("\n[dim]You can also use custom fine-tuned models by name[/dim]")


def find_command(input_text: str) -> Optional[str]:
    """Find command from input, handling aliases and typos."""
    input_lower = input_text.lower().strip()

    # Exact match
    if input_lower in COMMANDS:
        return input_lower

    # Check aliases
    for cmd, info in COMMANDS.items():
        if input_lower in info["aliases"] or input_lower == cmd:
            return cmd

    # Fuzzy match - simple prefix matching
    if input_lower.startswith("/"):
        for cmd in COMMANDS:
            if cmd.startswith(input_lower) or input_lower.startswith(cmd.split()[0]):
                return cmd

    return None


def suggest_command(input_text: str) -> Optional[str]:
    """Suggest similar command if input doesn't match."""
    input_lower = input_text.lower().strip()

    # Check for close matches
    for cmd in COMMANDS:
        cmd_base = cmd.split()[0] if " " in cmd else cmd
        if cmd_base.startswith(input_lower) or input_lower.startswith(cmd_base[:3]):
            return cmd

    return None


async def main_loop():
    """Main conversation loop with enhanced CLI."""
    # Configuration
    DB_PATH = "data/lifeline.db"
    SESSION_ID = "lifeline_user"
    HISTORY_FILE = Path("data/.lifeline_history")

    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)

    # Initialize database
    db = TimelineDatabase(DB_PATH)

    # Model configuration (can be changed via /model command)
    current_model = "gpt-4o"
    current_temperature = 0.7
    current_max_tokens = 1500

    # Create agent
    console.print("\n[cyan]Initializing LifeLine agent...[/cyan]")
    agent = create_lifeline_agent(
        DB_PATH, model=current_model, temperature=current_temperature, max_tokens=current_max_tokens
    )

    # Create persistent session
    session = SQLiteSession(SESSION_ID, f"data/{SESSION_ID}.db")

    # Fetch available models from API
    console.print("[dim]Fetching available models from OpenAI API...[/dim]")
    available_models = await fetch_available_models()

    # Setup prompt with history and autocomplete
    completer = CommandCompleter(db=db, available_models=available_models)
    # Ensure history file directory exists
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    history = FileHistory(str(HISTORY_FILE))

    # Custom style for prompt
    style = Style.from_dict(
        {
            "prompt": "bold #0087ff",  # Blue color for prompt
        }
    )

    session_prompt = PromptSession(
        completer=completer,
        history=history,
        auto_suggest=AutoSuggestFromHistory() if history else None,
        style=style,
        complete_while_typing=True,
    )

    console.print("[green]LifeLine is ready![/green]\n")
    print_welcome()

    # Main conversation loop
    while True:
        try:
            # Get user input with autocomplete (async version for event loop compatibility)
            # Use HTML formatting for prompt_toolkit
            user_input = await session_prompt.prompt_async(
                HTML("<b><style fg='blue'>You</style></b>: ")
            )
            user_input = user_input.strip()

            if not user_input:
                continue

            # Handle special commands
            cmd = find_command(user_input.split()[0] if user_input.split() else "")

            if cmd == "/quit":
                console.print("\n[yellow]Goodbye! Your memories are safely stored.[/yellow]")
                break

            elif cmd == "/help":
                print_welcome()
                continue

            elif cmd == "/stats":
                print_stats(db)
                continue

            elif cmd == "/clear":
                # Clear conversation history (not timeline data)
                session = SQLiteSession(SESSION_ID, f"data/{SESSION_ID}.db")
                console.print("[yellow]Conversation history cleared. Timeline data preserved.[/yellow]")
                continue

            elif cmd == "/categories":
                print_categories(db)
                continue

            elif cmd == "/recent":
                # Parse optional limit: /recent 5
                parts = user_input.split()
                limit = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
                print_recent(db, limit=limit)
                continue

            elif cmd == "/search":
                # Extract search query
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    console.print("[yellow]Usage: /search <query>[/yellow]")
                    console.print("[dim]Example: /search coffee[/dim]")
                    continue

                search_query = parts[1]
                console.print(f"\n[dim]Searching for: {search_query}[/dim]\n")

                # Show thinking indicator
                console.print("[dim]LifeLine is thinking...[/dim]")

                # Use agent to search
                result = await Runner.run(
                    agent,
                    f"Search for events related to: {search_query}",
                    session=session,
                    max_turns=5,
                )

                console.print(f"\n[bold magenta]LifeLine:[/bold magenta]")
                console.print(Markdown(result.final_output))
                continue

            elif cmd == "/model":
                # Refresh models list in case new ones were added
                available_models = await fetch_available_models()
                completer.available_models = available_models

                # Extract model name
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    # Show available models
                    print_models(current_model, available_models)
                    console.print(f"\n[dim]Current model: {current_model}[/dim]")
                    console.print("[yellow]Usage: /model <model_name>[/yellow]")
                    console.print("[dim]Example: /model gpt-4-turbo[/dim]")
                    continue

                new_model = parts[1].strip()

                # Validate model (allow custom models too)
                if new_model not in available_models:
                    # Check if it looks like a valid model name (custom fine-tuned models)
                    if not (
                        new_model.startswith("gpt-")
                        or new_model.startswith("o1-")
                        or new_model.startswith("ft:")
                        or ":" in new_model
                    ):
                        console.print(f"[yellow]Warning: '{new_model}' is not in the available models list[/yellow]")
                        console.print("[dim]You can still use it if it's a custom fine-tuned model[/dim]")
                        response = await session_prompt.prompt_async(
                            HTML("<b><style fg='yellow'>Continue anyway? (y/n)</style></b>: ")
                        )
                        if response.lower().strip() != "y":
                            continue

                # Switch model
                console.print(f"\n[cyan]Switching model to: {new_model}[/cyan]")
                console.print("[dim]Reinitializing agent...[/dim]")

                # Create new agent with new model
                agent = create_lifeline_agent(
                    DB_PATH,
                    model=new_model,
                    temperature=current_temperature,
                    max_tokens=current_max_tokens,
                )
                current_model = new_model

                console.print(f"[green]✓ Model switched to {new_model}[/green]")
                console.print("[dim]Note: Conversation history is preserved[/dim]\n")
                continue

            # Check if it's a command-like input that didn't match
            if user_input.startswith("/"):
                suggestion = suggest_command(user_input)
                if suggestion:
                    console.print(f"[yellow]Unknown command: {user_input}[/yellow]")
                    console.print(f"[dim]Did you mean: {suggestion}? (Type /help for all commands)[/dim]")
                else:
                    console.print(f"[yellow]Unknown command: {user_input}[/yellow]")
                    console.print("[dim]Type /help to see all available commands[/dim]")
                continue

            # Show thinking indicator
            console.print("\n[dim]LifeLine is thinking...[/dim]")

            # Run agent
            result = await Runner.run(
                agent,
                user_input,
                session=session,
                max_turns=10,  # Allow multi-turn tool use
            )

            # Display response
            console.print(f"\n[bold magenta]LifeLine:[/bold magenta]")
            console.print(Markdown(result.final_output))

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Press Ctrl+D or type /quit to exit LifeLine[/yellow]")
            continue

        except EOFError:
            # Ctrl+D pressed
            console.print("\n[yellow]Goodbye! Your memories are safely stored.[/yellow]")
            break

        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]")
            console.print("[yellow]Type /help for assistance[/yellow]")


async def main():
    """Entry point for LifeLine CLI."""
    try:
        await main_loop()
    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 10):
        console.print("[red]Error: LifeLine requires Python 3.10 or higher[/red]")
        sys.exit(1)

    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]LifeLine closed.[/yellow]")
