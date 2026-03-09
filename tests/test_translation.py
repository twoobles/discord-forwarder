from unittest.mock import MagicMock, patch

from bot.translation import translate


class TestTranslate:
    @patch("bot.translation.deepl.DeepLClient")
    def test_calls_deepl_with_correct_args(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_result = MagicMock()
        mock_result.text = "translated"
        mock_client.translate_text.return_value = mock_result

        result = translate("hello", "ZH", "fake-key")

        mock_client_cls.assert_called_once_with("fake-key")
        mock_client.translate_text.assert_called_once_with("hello", target_lang="ZH")
        assert result == "translated"

    @patch("bot.translation.deepl.DeepLClient")
    def test_returns_translated_text(self, mock_client_cls: MagicMock) -> None:
        mock_result = MagicMock()
        mock_result.text = "Hola mundo"
        mock_client_cls.return_value.translate_text.return_value = mock_result

        assert translate("Hello world", "ES", "key") == "Hola mundo"
