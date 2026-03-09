import os
from unittest.mock import patch

import pytest

from bot.config import load_settings


def _env_vars() -> dict[str, str]:
    return {
        "DISCORD_TOKEN": "test-discord-token",
        "WECHAT_WEBHOOK_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        "DEEPL_API_KEY": "test-deepl-key",
    }


class TestLoadSettings:
    def test_reads_all_vars(self) -> None:
        env = _env_vars()
        with patch.dict(os.environ, env, clear=False):
            settings = load_settings()

        assert settings.discord_token == env["DISCORD_TOKEN"]
        assert settings.wechat_webhook_url == env["WECHAT_WEBHOOK_URL"]
        assert settings.deepl_api_key == env["DEEPL_API_KEY"]

    @pytest.mark.parametrize(
        "missing_var", ["DISCORD_TOKEN", "WECHAT_WEBHOOK_URL", "DEEPL_API_KEY"]
    )
    def test_raises_on_missing_var(self, missing_var: str) -> None:
        env = _env_vars()
        del env[missing_var]
        with patch.dict(os.environ, env, clear=True), pytest.raises(KeyError, match=missing_var):
            load_settings()

    def test_settings_is_frozen(self) -> None:
        env = _env_vars()
        with patch.dict(os.environ, env, clear=False):
            settings = load_settings()

        with pytest.raises(AttributeError):
            settings.discord_token = "changed"  # type: ignore[misc]
