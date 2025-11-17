from utils.json_deterministic import _json_deterministic
from typing import Any
import hashlib


def fingerprint_meta(meta: Any) -> str:
    """
    Produce an **8-character** fingerprint of ``meta``.
    Any change – even a single character, whitespace, or key order – yields a
    different fingerprint.

    Implementation:
        * Serialize the whole meta dict with ``sort_keys=True`` → deterministic.
        * Feed the UTF-8 bytes to SHA-256.
        * Take the first 8 hex characters (32 bits → 2³² possibilities).
    """
    json_blob = _json_deterministic(meta).encode("utf-8")
    full_hash = hashlib.sha256(json_blob).hexdigest()   # 64 hex chars
    return full_hash[:8]                               # 8-char fingerprint
