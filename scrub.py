import time
import os
from datetime import datetime, timedelta

from twitter import (
    TwitterAPI,
    TwitterConfig,
    TwitterAPIException,
    TwitterRateLimitException,
)


def get_today_midnight() -> datetime:
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)


def scrub_tweets():
    now = get_today_midnight()
    older_than = now - timedelta(days=int(config.days_to_keep))

    print(f"Getting tweets older than {older_than}")
    tweets = api.get_tweets(older_than=older_than)

    total_tweets = len(tweets)
    failed_to_delete = 0
    for count, tweet in enumerate(tweets, start=1):
        print(f"Deleting tweet [{count}/{total_tweets}]")
        try:
            is_deleted = api.delete_tweet_by_tweet_id(tweet["id"])
            if not is_deleted:
                failed_to_delete += 1
        except TwitterAPIException:
            failed_to_delete += 1
        except TwitterRateLimitException as e:
            print(e)
            return

        time.sleep(1)

    if failed_to_delete == 0:
        print(f"{total_tweets} tweets have been successfully deleted.")
    else:
        print(f"{failed_to_delete} tweets failed to delete.")


if __name__ == "__main__":
    config = TwitterConfig.from_dotenv()
    api = TwitterAPI(config=config)

    if not os.path.isfile(".data/.refresh_token"):
        raise Exception(
            "A refresh token should be initially generated via server.py (see README)."
        )

    while True:
        scrub_tweets()
        print("Sleeping for 30 minutes")
        time.sleep(1800)  # 30 minutes
