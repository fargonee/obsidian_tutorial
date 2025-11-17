from typing import Dict, Any

from googleapiclient.errors import HttpError
from utils.root import root
from utils.phase_logger import phase
from utils.logger import log
from scripts.youtube.auth import get_authenticated_service
from utils.get_json import load_or_create_json


@phase("UPDATE YOUTUBE METADATA")
def update_youtube_metadata(key_64: str, new_meta: Dict[str, Any]) -> None:
    """
    Updates YouTube video metadata (title, description, tags, category) 
    for a single video identified by its 64-char fingerprint.
    
    Called automatically by track_meta_updates() when local meta has changed.
    """
    video_ids_path = root / "resources" / "video_ids.json"
    video_ids: Dict[str, str] = load_or_create_json(video_ids_path)

    youtube_id = video_ids.get(key_64)

    if not youtube_id:
        log.yellow(f"No YouTube ID found for {key_64[:12]}… → skipping metadata update")
        return

    # Prepare updated snippet
    snippet = {
        "title": new_meta["title"],
        "description": new_meta["description"],
        "tags": new_meta.get("tags", []),
        "categoryId": str(new_meta.get("categoryId", "27")),  # Ensure string
    }

    youtube = get_authenticated_service()

    try:
        log.blue.bold(f"Updating YouTube metadata → https://youtu.be/{youtube_id}")
        log.gray(f"Fingerprint: {key_64}")
        log.gray(f"Title: {snippet['title'][:60]}{'…' if len(snippet['title']) > 60 else ''}")

        request = youtube.videos().update(
            part="snippet",
            body={
                "id": youtube_id,
                "snippet": snippet
            }
        )
        response = request.execute()

        log.green.bold("SUCCESS → Metadata updated on YouTube")
        log.green(f"   Title: {response['snippet']['title']}")
        log.cyan(f"   Video: https://youtu.be/{youtube_id}")

    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        reason = error_details.get("reason", "unknown")

        log.red.bold("FAILED → YouTube API error")
        log.red(f"   Video ID: {youtube_id}")
        log.red(f"   Reason: {reason}")
        log.red(f"   Message: {e.content.decode()}")

        # Common non-fatal cases
        if reason in ("videoNotFound", "forbidden"):
            log.yellow("Video may have been deleted or access revoked. Keeping local record.")

    except Exception as e:
        log.red.bold("FATAL → Unexpected error during metadata update")
        log.red(f"   Fingerprint: {key_64}")
        log.red(f"   Error: {type(e).__name__}: {e}")
        raise  # Re-raise unexpected errors
