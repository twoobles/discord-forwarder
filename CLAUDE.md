# CLAUDE.md

## Project

discord-forwarder is a Python bot that bridges Discord messages to external chat platforms (initially WeChat Work), with optional translation via DeepL. The design is platform-agnostic: adding a new target platform means implementing one adapter class.

## Development Workflow

See WORKFLOW.md for the full branching and PR process.

## Architecture

```
bot/
├── main.py          # Entry point, Discord client setup
├── config.py        # All settings from env vars
├── store.py         # JSON persistence for followed channels
├── translation.py   # Pure DeepL wrapper — adapters never call this directly
├── adapters/
│   ├── base.py      # Abstract PlatformAdapter (send_text, send_image)
│   └── wechat.py    # WeChat Work webhook adapter (aiohttp POST)
└── commands/
    ├── forward.py   # /forward command
    └── follow.py    # /follow and /unfollow commands
tests/               # Mirrors bot/ structure
pyproject.toml
.env.example
```

**Key decisions:**
- `discord.py` with `app_commands` for slash commands
- `PlatformAdapter` ABC: `send_text(text: str)` and `send_image(data: bytes, filename: str)`
- WeChat Work adapter sends messages via incoming webhook (HTTP POST)
- Translation is a pure function called by command handlers — never inside adapters
- All secrets from environment variables only

## Commands

| Command | Behavior |
|---|---|
| `/forward [translate-to] <message>` | Forwards one message; accepts raw text, Discord message link, or a reply |
| `/follow [translate-to]` | Bot listens to the current channel and auto-forwards all messages |
| `/unfollow` | Stops listening to the current channel |

## Dev Commands

```bash
pytest                                  # Run tests
ruff check . && ruff format --check .  # Lint
ruff check --fix . && ruff format .    # Auto-fix
python -m bot.main                     # Run locally (requires .env)
```

## Rules

-   Run `pytest` before starting work and after every change
-   Run `ruff check .` after every change — it must pass before a task is done
-   Never hardcode secrets; use env vars and `python-dotenv`
-   Feature branches only — never commit to `main` directly
-   Branch names describe the feature: `add-wechat-adapter`, `implement-follow-command`
-   Type hints on all public functions