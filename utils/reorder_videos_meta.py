def reorder_video_meta(meta: dict) -> dict:
    """
    Returns a new dict sorted by (id, title).
    Keys are fingerprints; values are video meta dicts.
    """
    # We sort by:
    # 1. id (None goes last)
    # 2. title (None goes last)
    sorted_items = sorted(
        meta.items(),
        key=lambda kv: (
            kv[1].get("id") is None,
            kv[1].get("id"),
            kv[1].get("title") is None,
            kv[1].get("title") or ""
        )
    )
    return dict(sorted_items)
