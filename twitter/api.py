import base64
import hashlib
import os
import re
import typing
from datetime import datetime

import requests
from requests_oauthlib import OAuth2Session

from .config import TwitterConfig
from .exception import TwitterAPIException, TwitterRateLimitException

TWITTER_API_V2_URL = "https://api.twitter.com/2"
TWITTER_OAUTH_REDIRECT_URI = "http://127.0.0.1:8000/oauth/callback"
TWITTER_OAUTH_AUTHORIZATION_URL = "https://twitter.com/i/oauth2/authorize"
TWITTER_OAUTH_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
TWITTER_SCOPES = ["tweet.read", "users.read", "tweet.write", "offline.access"]


class TwitterAPI:
    _config: TwitterConfig = None
    _oauth2_session: OAuth2Session = None
    _code_verifier: str = None
    _code_challenge: str = None
    _token: typing.Dict = None

    def __init__(self, config: TwitterConfig):
        self._config = config
        self._oauth2_session = OAuth2Session(
            client_id=self._config.client_id,
            redirect_uri=TWITTER_OAUTH_REDIRECT_URI,
            scope=TWITTER_SCOPES,
        )

        code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
        code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
        self._code_verifier = code_verifier

        code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
        code_challenge = code_challenge.replace("=", "")
        self._code_challenge = code_challenge

    def get_user_id_from_handle(self, handle) -> str:
        response = requests.get(
            f"{TWITTER_API_V2_URL}/users/by/username/{handle}",
            headers={"Authorization": f"Bearer {self._config.bearer_token}"},
        )

        if response.status_code != 200:
            raise TwitterAPIException("Failed to retrieve twitter user ID")

        try:
            user_id = response.json()["data"]["id"]
        except KeyError:
            raise TwitterAPIException("Failed to retrieve twitter user ID")

        return user_id

    def get_tweets(self, older_than: datetime = None) -> typing.List[typing.Dict]:
        user_id = self.get_user_id_from_handle(self._config.twitter_handle)
        url = f"{TWITTER_API_V2_URL}/users/{user_id}/tweets?tweet.fields=created_at&max_results=50"

        if older_than is not None:
            url += f'&end_time={older_than.strftime("%Y-%m-%dT%H:%M:%SZ")}'

        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {self._config.bearer_token}"},
        )

        if response.status_code != 200:
            raise TwitterAPIException("Failed to retrieve tweets")

        try:
            tweets = response.json()["data"]
        except KeyError:
            raise TwitterAPIException("Failed to retrieve tweets")

        return tweets

    def delete_tweet_by_tweet_id(self, tweet_id: str) -> bool:
        if not self._token:
            self.refresh_token()

        access_token = self._token["access_token"]
        response = requests.delete(
            f"{TWITTER_API_V2_URL}/tweets/{tweet_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        print(response.status_code)
        print(response.json())

        if response.status_code == 429:
            raise TwitterRateLimitException("API Limit reached for this 15 min window")

        if response.status_code != 200:
            raise TwitterAPIException("Failed to delete tweet")

        try:
            is_deleted = response.json()["data"]["deleted"]
        except KeyError:
            raise TwitterAPIException("Failed to delete tweet")

        return is_deleted

    def get_oauth_authorization_url(self) -> str:
        url, _ = self._oauth2_session.authorization_url(
            TWITTER_OAUTH_AUTHORIZATION_URL,
            code_challenge=self._code_challenge,
            code_challenge_method="S256",
        )
        return url

    def get_oauth_token(self, code: str) -> typing.Dict:
        token = self._oauth2_session.fetch_token(
            token_url=TWITTER_OAUTH_TOKEN_URL,
            client_secret=self._config.client_secret,
            code_verifier=self._code_verifier,
            code=code,
        )
        return token

    def refresh_token(self):
        refresh_token = self._read_refresh_token_from_file()

        token = self._oauth2_session.refresh_token(
            client_id=self._config.client_id,
            client_secret=self._config.client_secret,
            token_url=TWITTER_OAUTH_TOKEN_URL,
            refresh_token=refresh_token,
        )
        self._token = token

        try:
            refresh_token = token["refresh_token"]
        except KeyError:
            raise Exception("Failed to retrieve refresh token")
        self.persist_refresh_token(refresh_token)

    @staticmethod
    def persist_refresh_token(refresh_token: str):
        with open(".data/.refresh_token", "w") as f:
            f.write(refresh_token)

    @staticmethod
    def _read_refresh_token_from_file() -> str:
        os.makedirs(".data", exist_ok=True)
        with open(".data/.refresh_token", "r") as f:
            refresh_token = f.read()
            return refresh_token
