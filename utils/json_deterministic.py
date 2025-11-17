import json
from typing import Any


def _json_deterministic(obj: Any) -> str:
    """
    Return a JSON string that is *exactly* the same for the same logical data,
    regardless of dict key order or whitespace.
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
