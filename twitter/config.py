from dataclasses import dataclass

import os
from dotenv import load_dotenv


def _get_required_os_env_var(envvar: str):
    try:
        val = os.environ[envvar]
    except KeyError:
        raise Exception(f"Did not supply required environment variable {envvar}")
    return val


@dataclass(kw_only=True)
class TwitterConfig:
    api_key: str
    api_secret: str
    bearer_token: str
    client_id: str
    client_secret: str
    twitter_handle: str
    days_to_keep: str

    @classmethod
    def from_dotenv(cls, dotenv_file: str = ".env"):
        load_dotenv(dotenv_file)
        return TwitterConfig(
            api_key=_get_required_os_env_var("API_KEY"),
            api_secret=_get_required_os_env_var("API_SECRET"),
            bearer_token=_get_required_os_env_var("BEARER_TOKEN"),
            client_id=_get_required_os_env_var("CLIENT_ID"),
            client_secret=_get_required_os_env_var("CLIENT_SECRET"),
            twitter_handle=_get_required_os_env_var("TWITTER_HANDLE"),
            days_to_keep=_get_required_os_env_var("DAYS_TO_KEEP"),
        )
