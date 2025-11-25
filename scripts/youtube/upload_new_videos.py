# scripts/youtube/upload.py
import json
import sys
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from utils.quota_limit_checker import is_quota_exceeded_error
from utils.root import root
from scripts.youtube.auth import get_authenticated_service
from utils.get_json import load_or_create_json
from utils.constants import video_type, sep
from utils.phase_logger import phase
from utils.logger import log
from utils.constants import PLAYLIST_ID


@phase("UPLOAD NEW VIDEOS (YOUTUBE) + ADD TO PLAYLIST")
def upload_new_videos() -> None:
    """
    Uploads videos in STRICT order from videos_meta.json.
    Stops immediately on ANY error to preserve tutorial sequence.
    """
    video_ids_path = root / "resources" / "video_ids.json"

    # Load with order preserved (critical!)
    videos_meta = load_or_create_json(root / "resources" / "videos_meta.json")
    video_ids = load_or_create_json(
        video_ids_path,
        default={fp: None for fp in videos_meta.keys()}
    )

    youtube = get_authenticated_service()

    try:
        for fingerprint, meta in videos_meta.items():
            filename = meta["filename"]
            video_path = root / "resources" / "final_videos" / f"{filename}{sep}{fingerprint}.{video_type}"

            # === Check if video file exists ===
            if not video_path.exists():
                log.red.bold(f"ERROR: Video file not found → {video_path}")
                log.red("Stopping entire upload to preserve tutorial order.")
                sys.exit(1)

            # === Skip already uploaded ===
            if video_ids.get(fingerprint):
                log.yellow(f"Already uploaded → {fingerprint[:8]}… → {video_ids[fingerprint]}")
                continue  # Still in order, just skip
                # Note: we use 'continue' here because previous ones were already in playlist

            log.blue.bold(f"Uploading → {meta['title']}")
            log.blue(f"   File: {video_path.name}")

            # === 1. Upload the video ===
            body = {
                "snippet": {
                    "title": meta["title"],
                    "description": meta["description"],
                    "tags": meta.get("tags", []),
                    "categoryId": meta.get("categoryId", "27"),
                },
                "status": {"privacyStatus": "public"},
            }

            media = MediaFileUpload(
                str(video_path),
                mimetype="video/*",
                resumable=True,
                chunksize=1024 * 1024,
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = request.execute()
            youtube_id = response["id"]
            video_ids[fingerprint] = youtube_id

            log.green.bold(f"SUCCESS → https://youtu.be/{youtube_id}")

            # === 2. Add to playlist immediately ===
            try:
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

                log.cyan.bold("Added to playlist")

            except HttpError as e:
                if is_quota_exceeded_error(e) is True:
                    log.red.bold("DAILY QUOTA LIMIT EXCEETED, We'll come back tomorrow")
                    continue
                else:
                    log.red.bold("FAILED TO ADD TO PLAYLIST → STOPPING")
                    log.red(f"Video: https://youtu.be/{youtube_id}")
                    log.red(f"Error: {e}")
                    raise

        # === All good → save progress ===
        video_ids_path.parent.mkdir(parents=True, exist_ok=True)
        with open(video_ids_path, "w", encoding="utf-8") as f:
            json.dump(video_ids, f, indent=4, ensure_ascii=False)

        log.cyan.bold("ALL VIDEOS UPLOADED AND ADDED IN PERFECT ORDER!")
        log.cyan(f"Playlist → https://www.youtube.com/playlist?list={PLAYLIST_ID}")

    except Exception as e:
        if is_quota_exceeded_error(e) is True:
            log.red.bold("DAILY QUOTA LIMIT EXCEETED, We'll come back tomorrow")
        else:
            # Critical: save progress before exiting
            log.red.bold("UPLOAD SEQUENCE STOPPED DUE TO ERROR")
            log.red.bold(str(e))
            log.red("Preserving tutorial order — fix issue and rerun.")

            with open(video_ids_path, "w", encoding="utf-8") as f:
                json.dump(video_ids, f, indent=4, ensure_ascii=False)

            log.yellow("Progress saved. Next run will continue from the next video.")
            sys.exit(1)