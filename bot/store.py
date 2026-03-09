import os
from json import dump, load


def load_channels(path: str) -> dict[int, str | None]:
    """Load followed channels from a JSON file. Returns empty dict if file missing."""
    try:
        with open(path) as file:
            # JSON keys are strings; convert back to int channel IDs
            return {int(k): v for k, v in load(file).items()}
    except FileNotFoundError:
        return {}


def save_channels(path: str, channels: dict[int, str | None]) -> None:
    """Persist followed channels to a JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w+") as file:
        dump(channels, file)
