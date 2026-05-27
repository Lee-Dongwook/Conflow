---
sidebar_position: 1
title: 설치 가이드
description: Conflow 개발 환경 설정 및 의존성 설치
---

# 설치 가이드

Conflow는 pnpm + Turborepo 모노레포와 Python(uv) 백엔드로 구성됩니다. 아래 단계를 따라 개발 환경을 구성하세요.

## 사전 요구사항

| 도구 | 최소 버전 | 설치 확인 |
|------|----------|----------|
| **Node.js** | 20.11.0+ | `node --version` |
| **pnpm** | 9.0+ | `pnpm --version` |
| **Python** | 3.13+ | `python --version` |
| **uv** | latest | `uv --version` |
| **Docker** | 24+ | `docker --version` |
| **Docker Compose** | v2+ | `docker compose version` |

### 도구 설치

```bash
# pnpm (Node.js가 이미 설치된 경우)
corepack enable
corepack prepare pnpm@9.15.0 --activate

# uv (Python 패키지 매니저)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 저장소 클론

```bash
git clone https://github.com/conflow/conflow.git
cd conflow
```

## Frontend 의존성 설치

모노레포 루트에서 pnpm으로 모든 workspace 패키지를 설치합니다:

```bash
pnpm install
```

이 명령은 다음 workspace의 의존성을 모두 설치합니다:
- `apps/web` -- Vite + React 프론트엔드
- `packages/core` -- 공유 인프라 (Axios, Zod, utils)
- `packages/ui` -- Atomic React 컴포넌트

## Backend 의존성 설치

```bash
cd server
uv sync --group agent --group dev
```

`--group agent`는 LangGraph/LangChain 에이전트 의존성을, `--group dev`는 pytest, ruff 등 개발 도구를 포함합니다.

## 데이터베이스 설정

### Docker로 PostgreSQL 실행

```bash
# 프로젝트 루트에서
docker compose up db
```

pgvector가 포함된 PostgreSQL 16이 포트 5432에서 실행됩니다.

기본 접속 정보:
- **Host**: localhost
- **Port**: 5432
- **Database**: conflow_db
- **User**: conflow_user
- **Password**: conflow_password

### 마이그레이션 적용

```bash
cd server
uv run alembic upgrade head
```

## 환경 변수 설정

```bash
cd server
cp .env.example .env
```

`.env` 파일에서 필요한 값을 설정합니다:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=conflow_db
DB_USER=conflow_user
DB_PASSWORD=conflow_password

# Supabase Auth
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# AI Agent
CONFLOW_AGENT_MODE=mock    # mock / llm / ollama / vllm
OPENAI_API_KEY=sk-...      # llm 모드 사용 시 필수

# Optional
REDIS_URL=redis://localhost:6379
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

:::tip
초기 개발 시에는 `CONFLOW_AGENT_MODE=mock`을 사용하세요. API 키 없이 모든 에이전트 기능을 테스트할 수 있습니다.
:::

## 설치 확인

```bash
# Frontend 빌드 확인
pnpm build

# Backend import 확인
cd server
uv run python -c "import main; print('main import ok')"

# Backend 테스트
uv run pytest -q -p no:cacheprovider
```

## 다음 단계

설치가 완료되었다면 [빠른 시작](/docs/getting-started/quick-start) 가이드로 이동하여 서비스를 실행해 보세요.
