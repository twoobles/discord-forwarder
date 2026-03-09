import deepl


def translate(text: str, target_lang: str, api_key: str) -> str:
    """Translate text using DeepL.

    Args:
        text: The text to translate.
        target_lang: DeepL language code (e.g. "ZH", "EN-US", "JA").
        api_key: DeepL API key. The library auto-detects Free vs Pro.

    Returns:
        The translated text.
    """
    client = deepl.DeepLClient(api_key)
    result = client.translate_text(text, target_lang=target_lang)
    return result.text
