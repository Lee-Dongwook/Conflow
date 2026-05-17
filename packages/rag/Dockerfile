# syntax=docker/dockerfile:1
FROM python:3.13-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY packages/rag/pyproject.toml packages/rag/uv.lock ./packages/rag/
COPY packages/rag/main.py ./packages/rag/
COPY packages/rag/src ./packages/rag/src/

WORKDIR /app/packages/rag

RUN uv sync --frozen --no-dev

ENV PATH="/app/packages/rag/.venv/bin:$PATH"
ENV PORT=8001

EXPOSE 8001

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port \"${PORT}\""]
