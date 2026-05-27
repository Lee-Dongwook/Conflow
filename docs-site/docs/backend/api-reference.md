---
sidebar_position: 2
title: API 참조
description: FastAPI 백엔드 REST API 엔드포인트 참조
---

# API 참조

Conflow의 백엔드는 FastAPI로 구축되어 자동 OpenAPI 문서를 제공합니다. 서버 실행 후 다음 URL에서 인터랙티브 문서를 확인할 수 있습니다:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 인증

대부분의 API는 Supabase Auth 기반 JWT 인증이 필요합니다.

```bash
Authorization: Bearer <supabase_access_token>
```

## 도메인별 엔드포인트

### Health Check

| Method | Path      | 설명           |
| ------ | --------- | -------------- |
| GET    | `/health` | 서버 상태 확인 |

### Users (`/users`)

| Method | Path                | 설명             |
| ------ | ------------------- | ---------------- |
| GET    | `/users/me`         | 현재 사용자 정보 |
| PUT    | `/users/me`         | 사용자 정보 수정 |
| GET    | `/users/me/profile` | 사용자 프로필    |

### Teams (`/teams`)

| Method | Path                         | 설명             |
| ------ | ---------------------------- | ---------------- |
| POST   | `/teams`                     | 팀 생성          |
| GET    | `/teams`                     | 사용자의 팀 목록 |
| GET    | `/teams/{team_uuid}`         | 팀 상세 정보     |
| PUT    | `/teams/{team_uuid}`         | 팀 정보 수정     |
| POST   | `/teams/{team_uuid}/members` | 팀 멤버 추가     |
| GET    | `/teams/{team_uuid}/members` | 팀 멤버 목록     |

### Sprints (`/teams/{team_uuid}/sprints`)

| Method | Path                                       | 설명          |
| ------ | ------------------------------------------ | ------------- |
| POST   | `/teams/{team_uuid}/sprints`               | 스프린트 생성 |
| GET    | `/teams/{team_uuid}/sprints`               | 스프린트 목록 |
| GET    | `/teams/{team_uuid}/sprints/{sprint_uuid}` | 스프린트 상세 |
| PUT    | `/teams/{team_uuid}/sprints/{sprint_uuid}` | 스프린트 수정 |

### Backlog (`/teams/{team_uuid}/backlog`)

| Method | Path                                     | 설명               |
| ------ | ---------------------------------------- | ------------------ |
| POST   | `/teams/{team_uuid}/backlog`             | 백로그 아이템 생성 |
| GET    | `/teams/{team_uuid}/backlog`             | 백로그 목록        |
| PUT    | `/teams/{team_uuid}/backlog/{item_uuid}` | 아이템 수정        |
| DELETE | `/teams/{team_uuid}/backlog/{item_uuid}` | 아이템 삭제        |

### Board (`/teams/{team_uuid}/board`)

| Method | Path                                   | 설명                       |
| ------ | -------------------------------------- | -------------------------- |
| GET    | `/teams/{team_uuid}/board`             | 칸반 보드 카드 목록        |
| POST   | `/teams/{team_uuid}/board`             | 카드 생성                  |
| PUT    | `/teams/{team_uuid}/board/{card_uuid}` | 카드 수정 (상태 변경 포함) |
| DELETE | `/teams/{team_uuid}/board/{card_uuid}` | 카드 삭제                  |

### Inbox (`/inbox`)

| Method | Path                       | 설명        |
| ------ | -------------------------- | ----------- |
| GET    | `/inbox`                   | 수신함 목록 |
| PUT    | `/inbox/{entry_uuid}/read` | 읽음 처리   |

### Week (`/teams/{team_uuid}/week`)

| Method | Path                                       | 설명               |
| ------ | ------------------------------------------ | ------------------ |
| GET    | `/teams/{team_uuid}/week`                  | 주간 마일스톤 목록 |
| POST   | `/teams/{team_uuid}/week`                  | 마일스톤 생성      |
| PUT    | `/teams/{team_uuid}/week/{milestone_uuid}` | 마일스톤 수정      |

### Retro (`/teams/{team_uuid}/retro`)

| Method | Path                                          | 설명             |
| ------ | --------------------------------------------- | ---------------- |
| GET    | `/teams/{team_uuid}/retro`                    | 회고 보드 목록   |
| POST   | `/teams/{team_uuid}/retro`                    | 회고 보드 생성   |
| POST   | `/teams/{team_uuid}/retro/{board_uuid}/items` | 회고 아이템 추가 |

### WebSocket

| Protocol | Path                     | 설명                 |
| -------- | ------------------------ | -------------------- |
| WS       | `/ws/huddle/{team_uuid}` | Huddle 음성 시그널링 |
| WS       | `/ws/dm/{user_uuid}`     | 다이렉트 메시지      |

## 에러 응답 형식

모든 에러 응답은 다음 형식을 따릅니다:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP 상태 코드

| 코드 | 설명                           |
| ---- | ------------------------------ |
| 200  | 성공                           |
| 201  | 생성 성공                      |
| 400  | 잘못된 요청 (유효성 검사 실패) |
| 401  | 인증 필요                      |
| 403  | 권한 없음                      |
| 404  | 리소스를 찾을 수 없음          |
| 409  | 충돌 (중복 등)                 |
| 422  | 처리 불가 (Pydantic 검증 실패) |
| 500  | 서버 내부 오류                 |

:::info
이 API 참조는 주요 엔드포인트의 개요입니다. 정확한 Request/Response 스키마와 파라미터는 Swagger UI (`http://localhost:8000/docs`)에서 확인하세요.
:::
