"""
API key management utility - prompts for key if missing/invalid and creates .env file.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from openai import OpenAI
from rich.console import Console
from rich.prompt import Prompt

console = Console()


def load_env_file(env_path: Path) -> dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


def save_env_file(env_path: Path, api_key: str) -> None:
    """Save API key to .env file."""
    env_path.parent.mkdir(parents=True, exist_ok=True)
    with open(env_path, "w") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")
        f.write("# Add other secrets here if life gets complicated.\n")


def validate_api_key(api_key: str) -> bool:
    """Validate API key by making a test API call."""
    from openai import AuthenticationError

    try:
        client = OpenAI(api_key=api_key)
        # Make a minimal API call to validate the key
        client.models.list(limit=1)
        return True
    except AuthenticationError:
        # Only return False for actual authentication errors
        return False
    except Exception as e:
        # For other errors (network, timeout, etc.), assume key might be valid
        # and warn the user but don't reject the key
        console.print(f"[yellow]Warning: Could not validate API key due to: {type(e).__name__}[/yellow]")
        console.print("[yellow]Assuming key is valid. If you encounter issues, check your key.[/yellow]")
        return True


def prompt_for_api_key() -> str:
    """Prompt user for API key interactively."""
    console.print("\n[bold yellow]OpenAI API Key Required[/bold yellow]")
    console.print("LifeLine needs an OpenAI API key to function.")
    console.print("Get your key from: [link]https://platform.openai.com/api-keys[/link]\n")
    
    while True:
        api_key = Prompt.ask(
            "Enter your OpenAI API key",
            password=True,  # Hide input
            default="",
        ).strip()
        
        if not api_key:
            console.print("[red]API key cannot be empty. Please try again.[/red]\n")
            continue
        
        # Validate the key
        console.print("[dim]Validating API key...[/dim]")
        if validate_api_key(api_key):
            console.print("[green]✓ API key is valid![/green]\n")
            return api_key
        else:
            console.print("[red]✗ Invalid API key. Please check and try again.[/red]\n")
            retry = Prompt.ask("Try again?", choices=["y", "n"], default="y")
            if retry.lower() != "y":
                console.print("[red]Cannot continue without a valid API key.[/red]")
                sys.exit(1)


def ensure_api_key(env_path: Optional[Path] = None) -> str:
    """
    Ensure API key is available, prompting user if missing/invalid.
    
    Checks in this order:
    1. OPENAI_API_KEY environment variable
    2. .env file in current directory or specified path
    3. Prompt user interactively
    
    Args:
        env_path: Optional path to .env file (defaults to ./.env)
    
    Returns:
        Valid API key string
    
    Exits if:
        - API key is invalid and user declines to retry
        - Running in non-interactive mode and key is missing
    """
    if env_path is None:
        env_path = Path(".env")
    
    # Check environment variable first
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        if validate_api_key(api_key):
            return api_key
        else:
            console.print("[yellow]Warning: OPENAI_API_KEY environment variable is invalid.[/yellow]")
    
    # Check .env file
    env_vars = load_env_file(env_path)
    if "OPENAI_API_KEY" in env_vars:
        api_key = env_vars["OPENAI_API_KEY"]
        if validate_api_key(api_key):
            return api_key
        else:
            console.print("[yellow]Warning: API key in .env file is invalid.[/yellow]")
    
    # Check if we're in interactive mode
    if not sys.stdin.isatty():
        console.print("[red]Error: No valid API key found and not running interactively.[/red]")
        console.print("Please set OPENAI_API_KEY environment variable or create .env file.")
        sys.exit(1)
    
    # Prompt user for API key
    api_key = prompt_for_api_key()
    
    # Save to .env file
    save_env_file(env_path, api_key)
    console.print(f"[green]✓ Saved API key to {env_path}[/green]\n")
    
    # Set environment variable for current process
    os.environ["OPENAI_API_KEY"] = api_key
    
    return api_key

