from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent

flow = InstalledAppFlow.from_client_secrets_file(
    (root / "youtube_client_secrets.json").as_posix(),
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)
creds = flow.run_local_server(port=0)

with open("token.pickle", "wb") as f:
    pickle.dump(creds, f)

print("token.pickle created successfully!")
print("Now run: base64 -w 0 token.pickle | pbcopy   (or just copy the output)")