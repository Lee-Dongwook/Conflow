---
sidebar_position: 99
title: 기여 가이드
description: Conflow 프로젝트에 기여하는 방법
---

# 기여 가이드

Conflow 프로젝트에 기여해 주셔서 감사합니다. 이 문서는 코드 기여 절차와 규칙을 설명합니다.

## 개발 환경 준비

[설치 가이드](/docs/getting-started/installation)를 따라 개발 환경을 구성한 후 시작하세요.

## 브랜치 전략

```
main
├── feat/feature-name      # 새 기능
├── fix/bug-description    # 버그 수정
├── refactor/target        # 리팩터링
├── docs/topic             # 문서 변경
└── chore/task             # 기타 작업
```

## 커밋 메시지 규칙

[Conventional Commits](https://www.conventionalcommits.org/)를 따릅니다. commitlint로 자동 검증됩니다.

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Type

| Type | 설명 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `style` | 코드 스타일 변경 (포맷 등) |
| `refactor` | 리팩터링 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 도구 등 기타 변경 |
| `hotfix` | 긴급 수정 |

### 예시

```
feat(agent): add retro_insights worker graph
fix(board): resolve card drag-and-drop ordering
docs(api): update sprint endpoints reference
refactor(core): extract database session factory
```

## 코딩 표준

### Frontend (TypeScript)

- **`const` only**: `let`을 사용하지 않습니다
- **No `any`**: `unknown` 또는 strict interface를 사용합니다
- **Zod 검증**: 모든 외부 데이터에 필수
- **Immutability**: `map`/`filter`/`reduce` 사용
- **순환 의존성 금지**: `packages/core` <- `packages/ui` <- `apps/web` 단방향만 허용

```bash
# 린트 실행
pnpm lint

# 타입 체크
pnpm typecheck
```

### Backend (Python)

- **ruff**: 린트 및 포맷 도구
- **줄 길이**: 100자
- **타겟**: Python 3.13+
- **규칙**: E, F, I, UP

```bash
cd server

# 린트 확인
uv run ruff check .

# 자동 포맷
uv run ruff format .

# 테스트
uv run pytest -q -p no:cacheprovider
```

### 도메인 모듈 추가 시

새 도메인을 추가할 때는 4-파일 패턴을 따릅니다:

```
server/src/app/{domain}/
├── api.py        # FastAPI 라우터
├── model.py      # SQLAlchemy 모델
├── schemas.py    # Pydantic 스키마
└── service.py    # 비즈니스 로직
```

## PR 체크리스트

PR을 제출하기 전에 다음을 확인하세요:

- [ ] 코드가 린트를 통과하는가 (`pnpm lint`, `uv run ruff check .`)
- [ ] 타입 체크를 통과하는가 (`pnpm typecheck`)
- [ ] 테스트가 통과하는가 (`pnpm test`, `uv run pytest`)
- [ ] 새 기능에 대한 테스트를 작성했는가
- [ ] 커밋 메시지가 Conventional Commits를 따르는가
- [ ] (해당 시) 마이그레이션 파일을 생성했는가
- [ ] (해당 시) 문서를 업데이트했는가

## 에이전트 개발 시 주의사항

### Mock 모드 우선
새 에이전트 기능을 개발할 때는 반드시 `CONFLOW_AGENT_MODE=mock`에서 먼저 동작을 확인하세요.

### Schema 정의 필수
모든 에이전트의 Input/Output은 명확한 스키마를 가져야 합니다. A2UI-Ready 설계를 위해 필수입니다.

### 스모크 테스트 작성
새 graph를 추가하면 `server/scripts/` 디렉터리에 스모크 테스트 스크립트를 함께 작성하세요.

```bash
# 스모크 테스트 실행 패턴
uv run python scripts/smoke_{graph_name}.py
```

## 도구

| 도구 | 용도 | 설정 |
|------|------|------|
| **ESLint** | JS/TS 린트 | `eslint.config.js` |
| **Prettier** | JS/TS 포맷 | `.prettierrc` |
| **ruff** | Python 린트/포맷 | `pyproject.toml` |
| **commitlint** | 커밋 메시지 검증 | `commitlint.config.js` |
| **husky** | Git hooks | `.husky/` |
| **lint-staged** | 스테이징된 파일 린트 | `package.json` |
| **Turborepo** | 모노레포 빌드 오케스트레이션 | `turbo.json` |
