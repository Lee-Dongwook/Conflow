# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir uv

# Build context must be the monorepo root (e.g. docker compose / docker build -f server/Dockerfile .)
COPY packages/rag /packages/rag
COPY server/pyproject.toml server/uv.lock ./
COPY server/alembic.ini ./
COPY server/alembic ./alembic/
COPY server/main.py ./
COPY server/src ./src/

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port \"${PORT}\""]
