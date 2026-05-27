---
sidebar_position: 2
title: 빠른 시작
description: Conflow 서비스를 로컬에서 실행하는 방법
---

# 빠른 시작

설치가 완료되었다면, 아래 방법 중 하나를 선택하여 Conflow를 실행할 수 있습니다.

## 방법 1: Docker Compose (권장)

모든 서비스를 한 번에 실행합니다:

```bash
docker compose up
```

실행되는 서비스:

| 서비스 | 포트 | 설명 |
|--------|------|------|
| **db** | 5432 | PostgreSQL 16 + pgvector |
| **backend** | 8000 | FastAPI 백엔드 |
| **rag** | 8001 | RAG 서비스 (pgvector) |
| **frontend** | 3000 | Vite + React 앱 |

## 방법 2: 개별 서비스 실행

### 1. 데이터베이스

```bash
docker compose up db
```

### 2. Backend

```bash
cd server
uv run uvicorn main:app --reload
```

FastAPI 서버가 `http://localhost:8000`에서 실행됩니다. API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

### 3. Frontend

```bash
# 모노레포 루트에서
pnpm --filter @conflow/web dev
```

Vite 개발 서버가 `http://localhost:3000`에서 실행됩니다.

### 4. Turborepo로 전체 실행

```bash
# 모노레포 루트에서
pnpm dev
```

Turborepo가 모든 workspace의 `dev` 스크립트를 병렬로 실행합니다.

## LangGraph Agent 실행

에이전트 시스템을 별도로 실행하려면:

```bash
cd server

# LangGraph dev 서버 (Studio + API :2024)
uv run langgraph dev
```

터미널에 출력되는 `https://smith.langchain.com/studio/?baseUrl=...` 링크로 LangGraph Studio에 접속할 수 있습니다.

### 에이전트 스모크 테스트

```bash
cd server

# meeting_summary 그래프 테스트
uv run python scripts/smoke_meeting_summary.py

# supervisor_graph 전체 플로우 테스트
uv run python scripts/smoke_supervisor_graph.py

# user_query 라우팅 테스트
uv run python scripts/smoke_user_query.py
```

## 주요 명령어 요약

### 모노레포 (루트)

| 명령어 | 설명 |
|--------|------|
| `pnpm dev` | 모든 서비스 실행 (Turborepo) |
| `pnpm build` | 전체 빌드 |
| `pnpm test` | 전체 테스트 |
| `pnpm typecheck` | TypeScript 타입 체크 |
| `pnpm lint` | 전체 린트 |

### Backend (server/)

| 명령어 | 설명 |
|--------|------|
| `uv run uvicorn main:app --reload` | FastAPI 개발 서버 |
| `uv run pytest` | Python 테스트 |
| `uv run ruff check .` | Python 린트 |
| `uv run ruff format .` | Python 포맷 |
| `uv run alembic upgrade head` | DB 마이그레이션 적용 |

### Database

| 명령어 | 설명 |
|--------|------|
| `docker compose up db` | PostgreSQL 실행 |
| `uv run alembic revision --autogenerate -m "desc"` | 마이그레이션 생성 |
