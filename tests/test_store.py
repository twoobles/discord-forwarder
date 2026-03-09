import json
from pathlib import Path

from bot.store import load_channels, save_channels


class TestLoadChannels:
    def test_returns_empty_dict_when_file_missing(self, tmp_path: Path) -> None:
        assert load_channels(str(tmp_path / "nonexistent.json")) == {}

    def test_reads_channels_with_int_keys(self, tmp_path: Path) -> None:
        path = tmp_path / "channels.json"
        path.write_text(json.dumps({"123": "ZH", "456": None}))

        result = load_channels(str(path))

        assert result == {123: "ZH", 456: None}


class TestSaveChannels:
    def test_writes_channels_to_file(self, tmp_path: Path) -> None:
        path = tmp_path / "channels.json"
        save_channels(str(path), {123: "ZH", 456: None})

        data = json.loads(path.read_text())
        assert data == {"123": "ZH", "456": None}

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        path = tmp_path / "nested" / "dir" / "channels.json"
        save_channels(str(path), {1: None})

        assert path.exists()

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        path = tmp_path / "channels.json"
        save_channels(str(path), {1: "ZH"})
        save_channels(str(path), {2: "EN-US"})

        data = json.loads(path.read_text())
        assert data == {"2": "EN-US"}


class TestRoundTrip:
    def test_save_then_load_preserves_data(self, tmp_path: Path) -> None:
        path = tmp_path / "channels.json"
        channels = {111: "ZH", 222: None, 333: "EN-US"}

        save_channels(str(path), channels)
        result = load_channels(str(path))

        assert result == channels
