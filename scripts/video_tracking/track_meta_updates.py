import json
from typing import Any, Dict

from utils.root import root
from utils.meta_fingerprinter import fingerprint_meta
from utils.get_json import load_or_create_json
from scripts.youtube.update_video_meta import update_youtube_metadata



videos_meta_path        = root / "resources" / "videos_meta.json"      # <-- typo in your original
meta_fingerprints_path  = root / "resources" / "meta_fingerprints.json" # 64-char key → 8-char fp



def track_meta_updates() -> None:
    """
    1. Load ``videos_meta.json``  →  { <64-char-key>: <meta-dict>, … }
    2. Load (or create) ``meta_fingerprints.json`` → { <64-char-key>: <8-char-fp>, … }
    3. For every entry:
           * compute fresh fingerprint of the current meta dict
           * compare with stored fingerprint
           * if different → call ``update_meta(key, meta)`` and store new fp
    """

    videos_meta: Dict[str, Any] = load_or_create_json(videos_meta_path)
    fingerprints: Dict[str, str] = load_or_create_json(meta_fingerprints_path)

    any_change = False

    for key_64, meta_dict in videos_meta.items():
        fresh_fp = fingerprint_meta(meta_dict)

        if fingerprints.get(key_64) == fresh_fp:
            # No change – nothing to do
            continue

        # ----------------------------------------------------------------
        # CHANGE DETECTED → trigger the update routine
        # ----------------------------------------------------------------
        update_youtube_metadata(key_64, meta_dict)

        # Store the new fingerprint
        fingerprints[key_64] = fresh_fp
        any_change = True

    # ------------------------------------------------------------------- #
    # Persist the (possibly updated) fingerprint file
    # ------------------------------------------------------------------- #
    if any_change:
        meta_fingerprints_path.write_text(
            json.dumps(fingerprints, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Fingerprints saved to {meta_fingerprints_path}")
    else:
        print("No meta changes detected.")