from scripts.youtube.upload_new_videos import upload_new_videos
from scripts.video_tracking.track_meta_updates import track_meta_updates



def publish_youtube():
    upload_new_videos()
    track_meta_updates()


if __name__ == "__main__":
    publish_youtube()
    track_meta_updates()