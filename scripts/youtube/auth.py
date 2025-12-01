# scripts/youtube/auth.py
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64
import tempfile

def get_authenticated_service():
    """
    Returns an authenticated YouTube Data API v3 service.
    Works perfectly in GitHub Actions with two secrets:
      • CLIENT_SECRETS_JSON  → base64-encoded client_secrets.json
      • YOUTUBE_REFRESH_TOKEN → raw refresh token string (1//04...)
    """
    # 1. Write the base64 client secrets to a temporary file
    client_secrets_b64 = os.getenv("CLIENT_SECRETS_JSON")
    if not client_secrets_b64:
        raise RuntimeError("Missing CLIENT_SECRETS_JSON secret")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(base64.b64decode(client_secrets_b64).decode())
        client_secrets_path = f.name

    # 2. Get the raw refresh token from secret
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    if not refresh_token:
        raise RuntimeError("Missing YOUTUBE_REFRESH_TOKEN secret")

    # 3. Define scopes (must be the same as when you got the refresh token)
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # 4. Build credentials from refresh token
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_path,
        scopes=SCOPES
    )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=flow.client_config["client_id"],
        client_secret=flow.client_config["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES   # ← Use the SCOPES list here, not flow.scopes
    )

    # Force refresh to get a valid access token
    if not creds.valid:
        creds.refresh(Request())

    # Clean up the temporary file
    os.unlink(client_secrets_path)

    # Return the YouTube service
    return build("youtube", "v3", credentials=creds)