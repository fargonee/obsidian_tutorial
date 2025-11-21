# save as get_refresh_token.py
from google_auth_oauthlib.flow import InstalledAppFlow


flow = InstalledAppFlow.from_client_secrets_file('youtube_client_secrets.json', scopes=['https://www.googleapis.com/auth/youtube.force-ssl'])
credentials = flow.run_local_server(port=8080)
print("Refresh Token:", credentials.refresh_token)