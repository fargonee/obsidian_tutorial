from utils.root import root
from utils.extract_fingerprint import extract_fingerprint
from utils.fingerprinter import take_fingerprint
from utils.make_valid_filename import make_valid_filename
from utils.constants import sep, video_type
from utils.logger import log
from utils.phase_logger import phase


bare_videos = root / "resources" / "bare_videos"







@phase("FINGERPRINT")
def ensure_videos_fingerprinted():
    log.blue.bold("Checking for new videos:")
    new_count = 0
    for video in bare_videos.glob(f"*.{video_type}"):
        fingerprint = extract_fingerprint(video.name)
        if fingerprint is None:
            log.green(f"New video found: {video.name}")
            new_count += 1

            fingerprint = take_fingerprint(video)
            # Use stem to get filename without extension
            stem = video.stem.split(sep)[0]  
            # Append fingerprint
            new_file_name = f"{stem}{sep}{fingerprint}"
            # Sanitize filename
            valid_filename = make_valid_filename(new_file_name)
            # Rename with original suffix
            video.rename(bare_videos / f"{valid_filename}{video.suffix}")
    log.green.bold(f"{new_count} new videos found and fingerprinted!")
