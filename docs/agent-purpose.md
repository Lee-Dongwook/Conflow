# Conflow 에이전트 목적 (LangGraph)

Conflow 에이전트는 **협업 관제탑 UI를 대체하는 것이 아니라**, 팀이 놓치기 쉬운 정보를 구조화해 **대시보드·보드·수신함에 넣을 수 있는 데이터**를 만드는 백엔드 워커입니다.

## 제품 맥락 (README / 와이어 기준)

| Pain | 에이전트가 할 일 |
|------|------------------|
| 병목·무임승차 | 회의/채팅에서 **막힌 일(Blocker)**·담당 공백을 추출해 알림·보드 후보로 제안 |
| 마감 망각 | 논의에서 **마감·다음 단계**를 구조화해 이번 주·인박스에 반영 가능한 형태로 출력 |
| 툴 피로 | Notion 대신 **한 줄 요약 + 액션 리스트** (MeetingSummary 와이어와 동일 스키마) |

Phase 2 MVP 에이전트 범위: **허들(음성) 종료 → 전사 텍스트 → AI 회의록** (`MeetingSummaryPage`와 동일 필드).

## 그래프 로드맵

| Graph ID | 상태 | 입력 | 출력 (A2UI / API) |
|----------|------|------|-------------------|
| `meeting_summary` | **로컬 구현 (v0)** | `meeting_title`, `transcript`, `team_context?` | `overview`, `bullets`, `decisions`, `actions[]`, `next_steps[]` |
| `blocker_triage` | 예정 | 스프린트 컨텍스트, 보드 카드, 인박스 | Blocker 후보 + 근거 |
| `retro_insights` | 예정 | 회고 카드 텍스트 | KPT 클러스터·투표 요약 |

## `meeting_summary` 파이프라인

```
START → validate_input → summarize → END
```

- **validate_input**: 전사 본문 필수, 길이 상한(토큰 보호).
- **summarize**:
  - `CONFLOW_AGENT_MODE=mock` (기본): API 키 없이 로컬 스모크·Studio 테스트.
  - `CONFLOW_AGENT_MODE=llm`: `OPENAI_API_KEY`로 구조화 요약 (와이어 스키마 고정).

향후: STT 어댑터 노드 추가, `backlog_items` MCP 툴로 액션 자동 등록.

## 로컬 실행 (오늘 목표)

`server/` 디렉터리에서:

```bash
# 1) 에이전트 의존성 포함 동기화
uv sync --group agent --group dev

# 2) (선택) LLM 사용 시
cp .env.example .env   # 이미 있으면 생략
# OPENAI_API_KEY=sk-...
# CONFLOW_AGENT_MODE=llm

# 3) LangGraph dev 서버 (Studio + API :2024)
uv run langgraph dev

# 4) 그래프만 빠르게 확인 (서버 없이)
uv run python scripts/smoke_meeting_summary.py
```

Studio: 터미널에 출력되는 `https://smith.langchain.com/studio/?baseUrl=...` 링크.

**샘플 입력** (`scripts/smoke_meeting_summary.py` 또는 Studio):

```json
{
  "meeting_title": "FE 스터디 — 스프린트 계획",
  "transcript": "이번 주는 보드 WIP 3으로 제한하기로 했고, 금요일 데모는 스테이징 배포와 스크린샷 1장을 완료 기준으로 한다. 김○○가 백로그 상위 3건 메타데이터를 보강한다.",
  "team_context": "대학 스터디 팀, 1주 스프린트"
}
```

## FastAPI와의 관계

- **지금**: LangGraph CLI (`langgraph dev`)가 Agent Server를 띄움. FastAPI(`main.py`)와 **별 포트** (8000 vs 2024).
- **다음**: FastAPI에서 `langgraph_sdk`로 `meeting_summary` run 호출 → 회의록 REST + DB 저장.
