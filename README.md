# discord-forwarder

A Discord bot that bridges messages to WeChat Work (企业微信) group chats, with optional DeepL translation.

## Features

- `/forward [translate-to] <message>` — forward a message, Discord message link, or a reply
- `/follow [translate-to]` — auto-forward every new message in the current channel
- `/unfollow` — stop auto-forwarding
- Supports text and image attachments
- Optional translation to Chinese or English via DeepL

## Architecture

```
bot/
├── main.py                 # Entry point, Discord client setup
├── config.py               # Settings from environment variables
├── store.py                # JSON persistence for followed channels
├── translation.py          # DeepL translation wrapper
├── adapters/
│   ├── base.py             # PlatformAdapter ABC
│   └── wechat.py           # WeChat Work webhook adapter
└── commands/
    ├── forward.py           # /forward slash command
    └── follow.py            # /follow and /unfollow commands
```

The bot is platform-agnostic by design — adding a new target platform means implementing a single `PlatformAdapter` subclass with `send_text` and `send_image`.

## Setup

```bash
# 1. Clone and install
git clone https://github.com/twoobles/discord-forwarder.git
cd discord-forwarder
pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Edit .env with your tokens (see below)

# 3. Run
python -m bot.main
```

### Environment variables

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Bot token from the [Discord Developer Portal](https://discord.com/developers/applications) |
| `WECHAT_WEBHOOK_URL` | WeChat Work group bot webhook URL |
| `DEEPL_API_KEY` | DeepL API key (Free or Pro) |
| `DISCORD_GUILD_ID` | *(optional)* Restrict slash commands to a single server for instant sync |

### WeChat Work webhook

1. Open a WeChat Work group chat
2. Go to group settings and add a **Group Bot** (群机器人)
3. Copy the webhook URL — it looks like `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...`

## Development

```bash
pytest                                  # Run tests
ruff check . && ruff format --check .  # Lint and format check
ruff check --fix . && ruff format .    # Auto-fix
```