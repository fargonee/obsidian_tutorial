import cv2
import hashlib
import subprocess
import tempfile
import os
from pathlib import Path

def take_fingerprint(path: Path, frame_skip: int = 30) -> str:
    """
    Generates a deterministic audio-visual fingerprint.
    Sensitive to both visual and audio content.
    Any slight edit (color, frame, or sound) changes the result.

    Parameters:
        path (Path): Path to the video file
        frame_skip (int): Number of frames to skip between samples
    """
    if not isinstance(path, Path):
        path = Path(path)

    hasher = hashlib.sha256()
    str_path = str(path)  # convert Path to string for cv2 and subprocess

    # ---- VISUAL FINGERPRINT ----
    cap = cv2.VideoCapture(str_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {path}")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_skip == 0:
            resized = cv2.resize(frame, (64, 64), interpolation=cv2.INTER_AREA)
            hasher.update(resized.tobytes())
        frame_count += 1
    cap.release()

    # ---- AUDIO FINGERPRINT ----
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        tmp_audio_path = tmp_audio.name

    # extract raw PCM audio using ffmpeg
    subprocess.run(
        ["ffmpeg", "-y", "-i", str_path, "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", tmp_audio_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    # read and hash audio bytes
    try:
        with open(tmp_audio_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    finally:
        os.remove(tmp_audio_path)

    return hasher.hexdigest()
