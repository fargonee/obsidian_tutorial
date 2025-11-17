from scripts.video_tracking.ensure_videos_fingerprinted import ensure_videos_fingerprinted
from scripts.video_tracking.ensure_videos_meta import ensure_videos_meta
from scripts.studio.create_thumbnail_text_layers import create_thumbnails
from scripts.studio.diversify_intro import diversify_intro
from scripts.studio.add_music_to_videos import add_music_to_all_videos
from scripts.studio.merge_intros_to_videos import merge_intros_to_videos

FORCE_REWRITE = True

def main():
    ensure_videos_fingerprinted()
    ensure_videos_meta()

    create_thumbnails(FORCE_REWRITE)
    diversify_intro(FORCE_REWRITE)

    add_music_to_all_videos(FORCE_REWRITE)

    merge_intros_to_videos(FORCE_REWRITE)



if __name__ == "__main__":
    main()