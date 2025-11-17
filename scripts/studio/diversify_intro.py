import subprocess

from utils.root import root
from utils.logger import log
from utils.phase_logger import phase



intro_video = root / "resources" / "intro.mkv"
thumb_text_layers_dir = root / "resources" / "thumbnail_text_layers"
output_dir = root / "resources" / "intros"
output_dir.mkdir(parents=True, exist_ok=True)

@phase("DIVERSIFY INTRO")
def diversify_intro(force_rewrite: bool = False):
    # === FORCE REWRITE CLEANUP ===
    if force_rewrite:
        for f in output_dir.iterdir():
            if f.is_file():
                f.unlink()
        log.yellow("Output folder cleared due to force_rewrite=True")

    # === VALIDATE ===
    if not intro_video.exists():
        log.red.bold(f"ERROR: Intro video not found: {intro_video}")
        return
    if not thumb_text_layers_dir.is_dir():
        log.red.bold(f"ERROR: Thumbnails folder not found: {thumb_text_layers_dir}")
        return

    # Get thumbnails
    thumbnails = sorted(
        [f for f in thumb_text_layers_dir.iterdir() if f.suffix.lower() == ".png"],
        key=lambda x: x.stem
    )
    if not thumbnails:
        log.red.bold("No PNG thumbnails found!")
        return

    log.blue.bold(f"Found {len(thumbnails)} thumbnails → overlaying 1:1 on intro...\n")

    # === PROCESS EACH ===
    for i, thumb in enumerate(thumbnails, 1):
        output_file = output_dir / f"{thumb.stem}.mkv"

        # Skip if already exists and not forcing
        if not force_rewrite and output_file.exists():
            log.yellow(f"[{i:02d}] Skipped (already exists): {output_file.name}")
            continue

        filter_complex = "[0:v][1:v]overlay=0:0"

        log.blue(f"[{i:02d}] {thumb.name} → {output_file.name}")

        cmd = [
            "ffmpeg", "-y",
            "-i", str(intro_video),
            "-i", str(thumb),
            "-filter_complex", filter_complex,
            "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
            "-c:a", "copy",
            str(output_file)
        ]

        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            log.green.bold(" [OK]")
        else:
            log.red.bold(" [FAILED]")

    log.green.bold(f"\nDONE! {len(thumbnails)} intros generated.")
    log.green(f"Location: {output_dir}")


if __name__ == "__main__":
    diversify_intro()
