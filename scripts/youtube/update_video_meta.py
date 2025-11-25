# scripts/youtube/update_meta.py
from typing import Dict, Any

from googleapiclient.errors import HttpError
from utils.root import root
from utils.logger import log
from scripts.youtube.auth import get_authenticated_service
from utils.get_json import load_or_create_json
from utils.constants import PLAYLIST_ID
from utils.quota_limit_checker import is_quota_exceeded_error


def update_youtube_metadata(key_64: str, new_meta: Dict[str, Any]) -> None:
    """
    Updates YouTube video metadata AND ensures the video exists in the main playlist.
    Called automatically when local meta changes.
    """
    video_ids_path = root / "resources" / "video_ids.json"
    video_ids: Dict[str, str] = load_or_create_json(video_ids_path)

    youtube_id = video_ids.get(key_64)
    if not youtube_id:
        log.yellow(f"[SKIP] No YouTube ID for {key_64[:10]}… (not uploaded yet)")
        return

    youtube = get_authenticated_service()

    # Prepare snippet
    snippet = {
        "title": new_meta["title"],
        "description": new_meta["description"],
        "tags": new_meta.get("tags", []),
        "categoryId": str(new_meta.get("categoryId", "27")),
    }

    try:
        log.blue.bold(f"Updating metadata → https://youtu.be/{youtube_id}")
        log.grey(f"   Fingerprint: {key_64}")
        log.grey(f"   Title: {snippet['title'][:70]}...")

        youtube.videos().update(
            part="snippet",
            body={"id": youtube_id, "snippet": snippet}
        ).execute()

        log.green.bold("Metadata updated successfully")

        # === Ensure video is in the playlist (idempotent) ===
        try:
            response = youtube.playlistItems().list(
                part="contentDetails,snippet",
                playlistId=PLAYLIST_ID,
                videoId=youtube_id,
                maxResults=1
            ).execute()

            if response.get("items"):
                log.cyan("Already in playlist")
            else:
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": PLAYLIST_ID,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": youtube_id
                            }
                        }
                    }
                ).execute()
                log.cyan.bold("Added back to playlist")
                log.cyan(f"   → https://www.youtube.com/playlist?list={PLAYLIST_ID}")

        except HttpError as playlist_err:
            if is_quota_exceeded_error(playlist_err):
                log.red.bold("DAILY QUOTA EXCEEDED – stopping further API calls for today")
                return  # Silent exit for the rest of this run
            else:
                log.red.bold("Failed to manage playlist membership")
                log.red(f"   Error: {playlist_err}")
                # Non-quota playlist errors are rare but not fatal — continue

    except HttpError as e:
        if is_quota_exceeded_error(e):
            log.red.bold("DAILY QUOTA EXCEEDED – metadata update skipped for this video")
            log.red("   We'll resume tomorrow when quota resets.")
            return  # Graceful early exit — no traceback, no noise

        # Any other HTTP error → loud
        try:
            details = e.error_details[0] if hasattr(e, "error_details") and e.error_details else {}
            reason = details.get("reason", "unknown")
        except Exception:
            reason = "unknown"

        log.red.bold("METADATA UPDATE FAILED")
        log.red(f"   Video: https://youtu.be/{youtube_id}")
        log.red(f"   Reason: {reason}")
        log.red(f"   Full error: {e}")

        if reason in ("videoNotFound", "forbidden", "videoDeleted"):
            log.yellow("Video no longer exists on YouTube. Keeping local record for now.")

    except Exception as e:
        # Truly unexpected → loud and let scheduler see the failure
        log.red.bold("FATAL UNEXPECTED ERROR in metadata update")
        log.red(f"   Video ID: {youtube_id}")
        log.red(f"   Error: {e}")
        raise  # Re-raise so cron/scheduler knows something went wrong


# Public hook
def update_meta(key_64: str, meta_dict: Dict[str, Any]) -> None:
    update_youtube_metadata(key_64, meta_dict)