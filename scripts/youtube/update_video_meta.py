# scripts/youtube/update_meta.py
from typing import Dict, Any

from googleapiclient.errors import HttpError
from utils.root import root
from utils.phase_logger import phase
from utils.logger import log
from scripts.youtube.auth import get_authenticated_service
from utils.get_json import load_or_create_json
from utils.constants import PLAYLIST_ID



@phase("UPDATE YOUTUBE METADATA + ENSURE IN PLAYLIST")
def update_youtube_metadata(key_64: str, new_meta: Dict[str, Any]) -> None:
    """
    Updates YouTube video metadata AND ensures the video exists in the main playlist.
    Called automatically when local meta changes.
    """
    video_ids_path = root / "resources" / "video_ids.json"
    video_ids: Dict[str, str] = load_or_create_json(video_ids_path)

    youtube_id = video_ids.get(key_64)
    if not youtube_id:
        log.yellow(f"[SKIP] No YouTube ID for {key_64[:10]}… (not uploaded)")
        return

    youtube = get_authenticated_service()

    # === 1. Update metadata (title, description, tags, etc.) ===
    snippet = {
        "title": new_meta["title"],
        "description": new_meta["description"],
        "tags": new_meta.get("tags", []),
        "categoryId": str(new_meta.get("categoryId", "27")),
    }

    try:
        log.blue.bold(f"Updating metadata → https://youtu.be/{youtube_id}")
        log.gray(f"   Fingerprint: {key_64}")
        log.gray(f"   Title: {snippet['title'][:70]}...")

        youtube.videos().update(
            part="snippet",
            body={"id": youtube_id, "snippet": snippet}
        ).execute()

        log.green.bold("Metadata updated on YouTube")

        # === 2. Ensure video is in the playlist (idempotent) ===
        try:
            # Check if already in playlist
            response = youtube.playlistItems().list(
                part="snippet",
                playlistId=PLAYLIST_ID,
                videoId=youtube_id,
                maxResults=1
            ).execute()

            if response["items"]:
                log.cyan("Already in playlist")
            else:
                # Add it (at the end — order is controlled by videos_meta.json order during upload)
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
                log.cyan.bold("RE-ADDED TO PLAYLIST")
                log.cyan(f"   → https://www.youtube.com/playlist?list={PLAYLIST_ID}")

        except HttpError as e:
            log.red.bold("FAILED to add/check playlist")
            log.red(f"   Error: {e}")

    except HttpError as e:
        error = e.error_details[0] if e.error_details else {}
        reason = error.get("reason", "unknown")

        log.red.bold("METADATA UPDATE FAILED")
        log.red(f"   Video: https://youtu.be/{youtube_id}")
        log.red(f"   Reason: {reason}")

        if reason in ("videoNotFound", "forbidden"):
            log.yellow("Video deleted or access revoked. Keeping local record.")

    except Exception as e:
        log.red.bold("FATAL ERROR in metadata update")
        log.red(f"   Error: {e}")
        raise


# Public hook (used by track_meta_updates.py)
def update_meta(key_64: str, meta_dict: Dict[str, Any]) -> None:
    update_youtube_metadata(key_64, meta_dict)