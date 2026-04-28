FROM python:3.14-slim-bookworm

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_CACHE_DIR=/app/.cache/uv

LABEL org.opencontainers.image.title="my-app"
LABEL org.opencontainers.image.description="FastAPI app using uv script"

RUN groupadd --system --gid 10001 app && \
    useradd --system \
      --uid 10001 \
      --gid 10001 \
      --home-dir /app \
      --create-home \
      app

COPY --chown=app:app ./src/app.py /app/app.py

RUN chmod 755 /app/app.py && \
    mkdir -p /app/.cache/uv && \
    chown -R app:app /app

USER 10001:10001

RUN --mount=type=cache,target=/app/.cache/uv,uid=10001,gid=10001 \
    /app/app.py --help

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

EXPOSE 8000

CMD ["/app/app.py"]
