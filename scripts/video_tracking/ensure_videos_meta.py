import json
from utils.root import root
from utils.get_json import load_or_create_json
from utils.reorder_videos_meta import reorder_video_meta
from utils.project import BRAND, PLAYLIST_DESCRIPTION, ADDRESS, TAGS
from utils.constants import video_type, sep
from utils.phase_logger import phase
from utils.logger import log

videos = root / "resources" / "bare_videos"
videos_meta = root / "resources" / "videos_meta.json"

@phase("ADD META")
def ensure_videos_meta():
    metas = load_or_create_json(videos_meta, {})
    new_count = 0
    for video in videos.glob(f"*.{video_type}"):
        fp = video.stem.split(sep)[-1]
        id = video.stem.split("_")[0]
        name = video.name.split(sep)[0]
        if metas.get(fp, None) is None:
            new_count += 1
            log.green(f"adding new meta for {video.stem}")
            metas[fp] = {
                "id": id,
                "title": name,
                "label": name.replace('_', ' '),
                "filename": name,
                "description": (
                    f"\n{name}"
                    f"\n{PLAYLIST_DESCRIPTION}"
                    f"\n{BRAND}"
                    f"\n{ADDRESS}"
                ),
                "tags": TAGS
            }
    log.blue.bold(f"Meta added to {new_count} new videos")
    ordered_metas = reorder_video_meta(metas)
    with videos_meta.open("w", encoding="utf-8") as f:
        json.dump(ordered_metas, f, indent=4, ensure_ascii=False)
