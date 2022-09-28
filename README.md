# tweet-scrubber
> Delete your tweets older than X days

## How does this work?
Using the Twitter API (V2) we get your tweets older than a certain date
(max 50 tweets at a time) and delete them.

OAuth 2.0. is used as an authentication method. To initially obtain a refresh
token we first boot a server which authorizes the application and retrieves the
refresh token for the first time. 

The script `scrub.py` uses that refresh token to obtain a valid token to delete
tweets. A rolling copy of the refresh token is kept.

## Setting up
1. Create a new project and application in the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Rename `env.example` to `.env`.
3. Copy the `API_KEY`, `API_SECRET` and `BEARER_TOKEN` value over to `.env` file.
4. Under the application edit the "User Authentication Settings" to
    - Under OAuth 2.0 Authentication make it a _Native App_.
    - Under App info, make the callback URL `http://127.0.0.1:8000/oauth/callback`
5. Click save, and copy the `CLIENT_ID` and `CLIENT_SECRET` over to the `.env` file.
6. In your terminal, boot the server via `make start-server`
7. In your browser, navigate to http://127.0.0.1:8000 and authorize the application
8. A refresh token will be saved to a file `.data/.refresh_token`
9. Complete the other missing fields such as `TWITTER_HANDLE` and `DAYS_TO_KEEP`
10. Run the scrubber script via `make run-docker`