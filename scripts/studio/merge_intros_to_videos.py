import subprocess

from utils.root import root
from utils.constants import video_type
from utils.logger import log
from utils.phase_logger import phase


@phase("FINAL MERGE")
def merge_intros_to_videos(force_rewrite: bool = False) -> None:
    intros_dir   = root / "resources" / "intros"
    sounded_dir  = root / "resources" / "sounded_videos"
    output_dir   = root / "resources" / "final_videos"
    output_dir.mkdir(exist_ok=True)

    # ------------------------------------------------------------------ #
    # 1. Gather intros
    # ------------------------------------------------------------------ #
    intros = sorted(intros_dir.glob(f"*.{video_type}"), key=lambda p: p.stem)

    if not intros:
        log.red.bold(f"No intro videos found in {intros_dir}")
        return

    log.blue.bold(f"Found {len(intros)} intro videos → merging with sounded videos...\n")

    # ------------------------------------------------------------------ #
    # 2. Process each pair
    # ------------------------------------------------------------------ #
    for idx, intro_file in enumerate(intros, 1):
        sounded_file = sounded_dir / f"{intro_file.stem}.{video_type}"
        if not sounded_file.exists():
            log.red(f"[{idx:02d}] Missing sounded video → {sounded_file.name}")
            continue

        final_file = output_dir / f"{intro_file.stem}.{video_type}"

        # ---- skip / force-rewrite handling --------------------------------
        if final_file.exists() and not force_rewrite:
            log.yellow(f"[{idx:02d}] SKIP: Already exists → {final_file.name}")
            continue
        if final_file.exists() and force_rewrite:
            final_file.unlink()

        # ---- logging ------------------------------------------------------
        log.blue.bold(f"[{idx:02d}] Merging intro + video:")
        log.blue(f"  Intro : {intro_file.name}")
        log.blue(f"  Main  : {sounded_file.name}")
        log.blue(f"  → {final_file.name}")

        # ---- ffmpeg command (filter_complex concat) -----------------------
        # ---- inside the loop, replace the whole ffmpeg command block ----
        cmd = [
            "ffmpeg", "-y",
            "-i", str(intro_file),      # stream 0
            "-i", str(sounded_file),    # stream 1
            "-filter_complex",
            # 1. Scale intro video to 1920x1080, pad if needed, set 60 fps
            "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60[introv]; "
            # 2. Main video is already 1920x1080@60fps → just pass through
            "[1:v]null[vmain]; "
            # 3. Concatenate the two prepared video streams
            "[introv][vmain]concat=n=2:v=1:a=0[vout]; "
            # 4. Concatenate audio (sample-rate will be unified by aac encoder)
            "[0:a][1:a]concat=n=2:v=0:a=1[aout]",
            "-map", "[vout]",
            "-map", "[aout]",
            # Re-encode video (required because of filtering)
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            # Re-encode audio (same as before)
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            str(final_file)
        ]
        # *** NEW: capture stderr so we can show the real error ***
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,      # <-- capture error output
            text=True                    # <-- return strings, not bytes
        )

        if result.returncode == 0:
            log.green.bold(f"  [OK] Saved {final_file.name}\n")
        else:
            # ---- show the exact FFmpeg message -------------------------
            log.red.bold(f"  [FAILED] Could not merge {intro_file.name}\n")
            log.red.bold("  FFmpeg stderr:\n")
            for line in result.stderr.strip().splitlines():
                log.red(f"    {line}")
            log.red("\n")

    # ------------------------------------------------------------------ #
    # 3. Done
    # ------------------------------------------------------------------ #
    log.green.bold(f"DONE. Final videos are in: {output_dir}")


if __name__ == "__main__":
    merge_intros_to_videos()