start-server:
	uvicorn server:app

build-docker:
	docker build -t tweet-scrubber .

shell-docker: build-docker
	docker run -v '${PWD}/.data:/app/.data' --env-file=.env -it tweet-scrubber bash

run-docker: build-docker
	docker run -v '${PWD}/.data:/app/.data' --env-file=.env -t tweet-scrubber
