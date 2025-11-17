import subprocess
from utils.logger import log
from utils.root import root
from utils.phase_logger import phase
from utils.constants import video_type

bare_videos = root / "resources" / "bare_videos"
music_file = root / "resources" / "background.mp3"

output_dir = root / "resources" / "sounded_videos"
output_dir.mkdir(parents=True, exist_ok=True)

@phase("ADD MUSIC")
def add_music_to_all_videos(force_rewrite: bool = False):
    if not music_file.exists():
        log.red.bold(f"ERROR: Background music not found: {music_file}")
        return

    # === FORCE REWRITE CLEANUP ===
    if force_rewrite:
        for f in output_dir.iterdir():
            if f.is_file():
                f.unlink()
        log.yellow("Output folder cleared due to force_rewrite=True")

    log.blue.bold("Adding music to all videos...\n")

    # Select input videos
    input_videos = sorted(bare_videos.glob(f"*.{video_type}"))

    if not input_videos:
        log.red.bold("No matching videos found in bare_videos/")
        return

    for i, file in enumerate(input_videos, 1):
        output_file = output_dir / file.name

        # Skip existing when not forcing
        if not force_rewrite and output_file.exists():
            log.yellow(f"[{i:02d}] Skipped (already exists): {output_file.name}")
            continue

        log.blue(f"[{i:02d}] {file.name} → {output_file.name}", end="")

        # === MUSIC ADDING LOGIC (start at 0) ===
        # We loop the background track and mix with original audio
        cmd = [
            "ffmpeg", "-y",
            "-i", str(file),              # Video with original audio
            "-i", str(music_file),        # Music start at 0
            "-filter_complex",
            # Loop music if shorter than video
            "[1:a]aloop=loop=-1:size=0[music]; "
            "[music]volume=0.30[music_low]; "
            "[0:a][music_low]amix=inputs=2:duration=first[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "256k",
            "-shortest",
            str(output_file)
        ]

        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            log.green.bold(" [OK]")
        else:
            log.red.bold(" [FAILED]")

    log.green.bold("\nDONE! All videos processed.")
    log.green(f"Location: {output_dir}")


if __name__ == "__main__":
    add_music_to_all_videos()
