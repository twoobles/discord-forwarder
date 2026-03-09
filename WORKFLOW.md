# WORKFLOW.md

## Branch Strategy

- `main` is stable. Never commit directly to it.
- One branch per feature, named after what's being built:
  - Good: `add-wechat-adapter`, `implement-follow-command`, `deepl-translation`
  - Avoid: `fix`, `wip`, `changes`

## Standard Feature Flow

```bash
# 1. Start from main
git checkout main && git pull
git checkout -b your-feature-name

# 2. Verify baseline — all tests must pass before touching anything
pytest

# 3. Implement in small, logical commits

# 4. After every meaningful change
pytest && ruff check . && ruff format --check .

# 5. Open a PR into main — no merge without green tests and lint
```

## Commit Practices

-   Imperative present tense: `add PlatformAdapter base class`, `fix image forwarding for PNG`
-   One logical change per commit
-   Never commit `.env` or any credentials

## Adding a New Platform Adapter

1.  Create `bot/adapters/<platform>.py`, subclass `PlatformAdapter`
2.  Implement `send_text(text: str)` and `send_image(data: bytes, filename: str)`
3.  Wire into `bot/config.py` — command handlers need no changes
4.  Add tests in `tests/adapters/test_<platform>.py`
5.  Update `.env.example` with new required vars
6.  Run `pytest` and `ruff check .` before opening a PR

## Test & Lint Gates

| When | Required |
|---|---|
| Before starting work | `pytest`
| After every change |`pytest` + `ruff check .` + `ruff format --check .`
| Before opening a PR | Both, clean

## Environment Setup

```bash
cp .env.example .env   # Populate with Discord, WeChat, DeepL tokens
pip install -e ".[dev]"
```