from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from twitter import TwitterAPI, TwitterConfig

app = FastAPI()

config = TwitterConfig.from_dotenv()
api = TwitterAPI(config)


@app.get("/")
def token():
    authorization_url = api.get_oauth_authorization_url()
    return RedirectResponse(authorization_url)


@app.get("/oauth/callback")
def callback(code: str):
    oauth_token = api.get_oauth_token(code)
    try:
        refresh_token = oauth_token["refresh_token"]
    except KeyError:
        raise Exception("Failed to retrieve refresh token")
    api.persist_refresh_token(refresh_token)
    return {"success": True, "message": "refresh token saved to .refresh_token file"}
