# LifeLine Quick Start Guide

Get started with LifeLine in under 2 minutes using UV!

## 1. Install UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Set Up LifeLine

```bash
# Navigate to the project directory
cd agentsdk

# Install dependencies (creates .venv automatically)
uv sync

# Set your OpenAI API key
export OPENAI_API_KEY='sk-...'  # Replace with your key
```

## 3. Run LifeLine

```bash
uv run python main.py
```

That's it! You'll see a welcome message and can start logging memories.

## First Steps

Try these commands to get started:

```
> Log: Started learning the OpenAI Agents SDK today. It's pretty cool!
> What events do I have?
> /stats
```

## Useful Commands

### Running the CLI
```bash
uv run python main.py
```

### Running Examples
```bash
uv run python examples/example_usage.py
```

### Running MCP Server
```bash
uv run python -m lifeline.mcp_server
```

### Development

```bash
# Format code
uv run black lifeline/

# Lint code
uv run ruff check lifeline/

# Type check
uv run mypy lifeline/

# Run tests (when implemented)
uv run pytest
```

## Tips

1. **Set API key permanently** - Add to your shell profile:
   ```bash
   echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **View your databases** - Use a SQLite browser:
   ```bash
   # Install sqlitebrowser (macOS)
   brew install --cask db-browser-for-sqlite

   # Open your timeline
   open data/lifeline.db
   ```

3. **Backup your data** - Simply copy the .db files:
   ```bash
   cp data/lifeline.db data/lifeline_backup_$(date +%Y%m%d).db
   cp data/lifeline_user.db data/lifeline_user_backup_$(date +%Y%m%d).db
   ```

4. **Use aliases** - Make it easier to run:
   ```bash
   alias lifeline="cd ~/agentsdk && uv run python main.py"
   ```

## Next Steps

- Read the full [README.md](../README.md) for detailed documentation
- Run [examples/example_usage.py](../examples/example_usage.py) to see programmatic usage
- Customize categories and tools in `lifeline/tools.py`
- Set up the MCP server for timeline visualization

Enjoy preserving your memories with LifeLine!
