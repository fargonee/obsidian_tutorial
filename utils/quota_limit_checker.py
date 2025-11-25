from googleapiclient.errors import HttpError
import json

def is_quota_exceeded_error(e: HttpError) -> bool:
    """Detect YouTube daily quota exhaustion (403 quotaExceeded) OR daily upload limit (400 uploadLimitExceeded).
    Both block operations until the next day — treat as silent skips for scheduled runs.
    """
    if not isinstance(e, HttpError):
        return False

    try:
        content = e.content.decode("utf-8")
        error_json = json.loads(content)
        for error in error_json.get("error", {}).get("errors", []):
            reason = error.get("reason")
            if reason in ("quotaExceeded", "uploadLimitExceeded"):
                return True
    except Exception:
        pass

    # Fallback: raw byte checks (reliable for quick detection)
    return b"quotaExceeded" in e.content or b"uploadLimitExceeded" in e.content