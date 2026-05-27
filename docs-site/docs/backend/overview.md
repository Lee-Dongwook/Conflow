---
sidebar_position: 1
title: 백엔드 가이드
description: FastAPI + SQLAlchemy 2 백엔드 아키텍처 및 도메인 구조
---

# 백엔드 가이드

Conflow의 백엔드는 **FastAPI + SQLAlchemy 2 (async) + PostgreSQL 16**으로 구축되었습니다. `server/` 디렉터리에 위치하며, **uv**로 Python 의존성을 관리합니다.

## 프로젝트 구조

```
server/
├── src/app/
│   ├── core/               # 인프라 레이어
│   │   ├── config.py       # 환경 변수 설정
│   │   ├── database.py     # async SQLAlchemy 세션
│   │   ├── security.py     # JWT 인증
│   │   ├── verify_token.py # Supabase 토큰 검증
│   │   ├── llm_factory.py  # LLM 모델 팩토리
│   │   ├── middlewares.py   # CORS, 로깅 미들웨어
│   │   ├── exceptions.py   # 커스텀 예외
│   │   ├── guardrails.py   # AI 가드레일
│   │   └── schemas.py      # 공통 Pydantic 스키마
│   │
│   ├── agent/graphs/       # LangGraph Multi-Agent
│   │   ├── supervisor_graph.py
│   │   ├── user_query.py
│   │   ├── meeting_summary.py
│   │   ├── blocker_triage.py
│   │   ├── retro_insights.py
│   │   ├── file_analysis.py
│   │   ├── base_agent_state.py
│   │   ├── workers.py
│   │   └── schemas.py
│   │
│   ├── sandbox/            # AI 런타임 보안
│   ├── common/             # 횡단 관심사
│   │   ├── idempotency     # Redis 기반 멱등성
│   │   ├── circuit_breaker # 서킷 브레이커
│   │   └── caching         # 캐싱
│   │
│   ├── websockets/         # 실시간 통신
│   │
│   └── [도메인 모듈]/
│       ├── user/           # 사용자
│       ├── team/           # 팀
│       ├── sprint/         # 스프린트
│       ├── backlog/        # 백로그
│       ├── board/          # 칸반 보드
│       ├── inbox/          # 인박스
│       ├── week/           # 주간 마일스톤
│       ├── retro/          # 회고
│       └── planning/       # 플래닝
│
├── alembic/                # DB 마이그레이션
├── tests/                  # pytest 테스트
├── scripts/                # 스모크 테스트
├── main.py                 # FastAPI 엔트리포인트
├── pyproject.toml          # uv 프로젝트 설정
└── langgraph.json          # LangGraph 설정
```

## 도메인 모듈 패턴

각 도메인은 동일한 4-파일 패턴을 따릅니다:

```
server/src/app/{domain}/
├── api.py        # FastAPI 라우터 (엔드포인트 정의)
├── model.py      # SQLAlchemy ORM 모델
├── schemas.py    # Pydantic 스키마 (Request/Response DTO)
└── service.py    # 비즈니스 로직
```

### api.py

```python
from fastapi import APIRouter, Depends
from .schemas import CreateTeamRequest, TeamResponse
from .service import TeamService

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=TeamResponse)
async def create_team(
    request: CreateTeamRequest,
    service: TeamService = Depends(),
):
    return await service.create(request)
```

### model.py

```python
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from src.app.core.base import Base

class Team(Base):
    __tablename__ = "teams"

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    # ...
```

### schemas.py

```python
from pydantic import BaseModel

class CreateTeamRequest(BaseModel):
    name: str
    description: str | None = None

class TeamResponse(BaseModel):
    uuid: str
    name: str

    model_config = {"from_attributes": True}
```

### service.py

```python
from sqlalchemy.ext.asyncio import AsyncSession
from .model import Team
from .schemas import CreateTeamRequest

class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, request: CreateTeamRequest) -> Team:
        team = Team(**request.model_dump())
        self.session.add(team)
        await self.session.commit()
        return team
```

## 핵심 인프라

### 데이터베이스 (core/database.py)

비동기 SQLAlchemy 세션을 관리합니다. `asyncpg`를 PostgreSQL 드라이버로 사용합니다.

### 인증 (core/security.py, core/verify_token.py)

Supabase Auth와 연동된 JWT 기반 인증입니다. 요청 헤더의 Bearer 토큰을 검증합니다.

### LLM Factory (core/llm_factory.py)

`CONFLOW_AGENT_MODE`에 따라 적절한 LLM 인스턴스를 생성합니다. 모델 교체가 용이한 팩토리 패턴을 사용합니다.

### 횡단 관심사 (common/)

- **멱등성**: Redis 기반으로 동일 요청의 중복 처리를 방지
- **서킷 브레이커**: 외부 서비스 장애 시 빠른 실패 반환
- **캐싱**: 자주 조회되는 데이터의 응답 속도 향상

## 코딩 표준

### Python 스타일

- **ruff** 린터/포매터 사용
- 줄 길이: 100자
- 타겟: Python 3.13+
- 규칙: E, F, I, UP

```bash
# 린트 확인
uv run ruff check .

# 자동 포맷
uv run ruff format .
```

### 테스트

```bash
# 전체 테스트
uv run pytest

# 특정 파일
uv run pytest tests/test_health.py

# 상세 출력
uv run pytest -v -p no:cacheprovider
```

## 개발 서버

```bash
cd server

# FastAPI 개발 서버 (포트 8000)
uv run uvicorn main:app --reload

# LangGraph 에이전트 서버 (포트 2024)
uv run langgraph dev
```

API 문서는 서버 실행 후 `http://localhost:8000/docs` (Swagger UI) 또는 `http://localhost:8000/redoc` (ReDoc)에서 확인할 수 있습니다.
