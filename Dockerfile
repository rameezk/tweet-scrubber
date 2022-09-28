FROM python:3.10 as venv
WORKDIR /build
COPY requirements.txt .
RUN python -m venv --copies /build/.venv && \
    . .venv/bin/activate && \
    pip install -U pip && \
    pip install -r requirements.txt

FROM python:3.10-slim as runner
WORKDIR /app

COPY --from=venv /build/.venv .venv
ENV PATH /app/.venv/bin:$PATH

COPY twitter ./twitter
COPY scrub.py entrypoint.sh ./

ENTRYPOINT ["./entrypoint.sh"]