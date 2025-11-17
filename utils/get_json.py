from pathlib import Path
import json


def load_or_create_json(path: Path, default=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8") as f:
            json.dump(default or {}, f, indent=4)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
