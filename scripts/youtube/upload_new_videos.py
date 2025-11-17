import json
from googleapiclient.http import MediaFileUpload

from utils.root import root
from scripts.youtube.auth import get_authenticated_service
from utils.get_json import load_or_create_json
from utils.constants import video_type
from utils.phase_logger import phase
from utils.logger import log
from utils.constants import sep


@phase("UPLOAD NEW VIDEOS (YOUTUBE)")
def upload_new_videos() -> None:
    """
    Scans videos_meta.json and uploads any videos that don't yet have a YouTube ID
    recorded in video_ids.json. Updates video_ids.json with new YouTube video IDs.
    """
    video_ids_path = root / "resources" / "video_ids.json"

    videos_meta = load_or_create_json(root / "resources" / "videos_meta.json")
    video_ids = load_or_create_json(video_ids_path, {fp: None for fp in videos_meta.keys()})



    youtube = get_authenticated_service()

    for fingerprint, meta in videos_meta.items():
        filename = meta["filename"]
        video_path = root / "resources" / "final_videos" / f"{filename}{sep}{fingerprint}.{video_type}"

        if not video_path.exists():
            log.red.bold(f"Video file not found: {video_path}")
            continue

        if video_ids.get(fingerprint):
            log.yellow(f"Already uploaded → {fingerprint[:8]}… → {video_ids[fingerprint]}")
            continue

        # Prepare upload request body
        body = {
            "snippet": {
                "title": meta["title"],
                "description": meta["description"],
                "tags": meta.get("tags", []),
                "categoryId": meta.get("categoryId", "27"),  # Education
            },
            "status": {
                "privacyStatus": "public"  # Change to 'private' or 'unlisted' if needed
            },
        }

        try:
            log.blue.bold(f"Uploading → {video_path.name}")

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(
                    str(video_path),
                    mimetype="video/*",
                    resumable=True,
                    chunksize=1024 * 1024,  # 1MB chunks – helps with large files
                ),
            )

            response = request.execute()
            youtube_id = response["id"]

            video_ids[fingerprint] = youtube_id

            log.green.bold(f"SUCCESS → https://youtu.be/{youtube_id}")
            log.green(f"Fingerprint: {fingerprint}")

        except Exception as e:
            log.red.bold(f"FAILED → {video_path.name}")
            log.red(f"Error: {e}")
            # Continue with next video instead of crashing
            continue

    # Persist updated video IDs
    video_ids_path.parent.mkdir(parents=True, exist_ok=True)
    with open(video_ids_path, "w", encoding="utf-8") as f:
        json.dump(video_ids, f, indent=4, sort_keys=True, ensure_ascii=False)

    log.cyan.bold("Upload phase completed. video_ids.json updated.")