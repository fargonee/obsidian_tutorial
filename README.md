# Obsidian Tutorial (Uzbek)

Automates publishing Obsidian tutorial videos to YouTube.

## Setup
1. Add videos to `/videos/`, thumbnails to `/thumbnails/`, metadata JSON to `/metadata/`.
2. Push to main → GitHub Actions syncs with YouTube playlist.

## Metadata Example (`metadata/001_yangi_hamyon_ochish.json`)
{
  "title": "001. Yangi hamyon ochish",
  "description": "Obsidian darsligi: Yangi hamyon ochish bo'yicha qo'llanma. Uzbek tilida.",
  "tags": ["obsidian", "uzbek", "tutorial"],
  "categoryId": "27"  // YouTube Education category
}

## Automation
- On push: Compares local files with YouTube playlist.
- New: Upload video + thumbnail + metadata.
- Changed: Update metadata/thumbnail (or re-upload video if changed).
- Missing: Delete from YouTube.

## Secrets
- YOUTUBE_CLIENT_SECRETS: client_secrets.json content
- YOUTUBE_REFRESH_TOKEN: From auth
- YOUTUBE_PLAYLIST_ID: Your playlist ID