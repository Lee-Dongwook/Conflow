# WebSocket 시스템 점검 보고서

> **작성일**: 2026-05-31
> **대상**: `server/src/app/websockets/`
> **목적**: Huddle (Google Meet-like) + DM (Slack DM-like)

---

## 1. 현재 아키텍처 요약

### 파일 구조

```
server/src/app/websockets/
├── api.py                 # FastAPI WebSocket 엔드포인트 (/ws/signal/{room_id})
├── hub.py                 # SignalingHub - 인메모리 room 기반 JSON relay
├── schemas.py             # Pydantic 시그널링 메시지 스키마
├── session_manager.py     # HuddleSessionManager + aiortc RTCPeerConnection (미연결)
├── media_processor.py     # 서버측 오디오 수신 → STT 파이프라인 (미연결)
├── agent_orchestrator.py  # STT 결과 → LangGraph agent 실행 (미연결)
├── signal.py              # 로컬 테스트용 standalone 시그널링 서버 (port 8765)
├── peer.py                # CLI 테스트용 WebRTC peer 헬퍼
├── initiator.py           # CLI offerer 테스트
└── receiver.py            # CLI answerer 테스트
```

### 두 레이어의 분리

| 레이어                                                                                           | 역할                                              | 상태                                  |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------- | ------------------------------------- |
| **SignalingHub** (`hub.py` + `api.py`)                                                           | 범용 JSON relay. 메시지 파싱 없이 raw string 전달 | 동작하지만 보안 미비                  |
| **HuddleSessionManager** (`session_manager.py` → `media_processor.py` → `agent_orchestrator.py`) | aiortc 기반 서버측 WebRTC + STT + LangGraph       | **Dead code** - API에서 호출되지 않음 |

---

## 2. 치명적 문제 (P0)

### 2.1 HuddleSessionManager가 Dead Code

`api.py`는 `SignalingHub`만 사용하며, `HuddleSessionManager`를 호출하는 코드가 없음. 서버측 오디오 처리 파이프라인 전체가 연결되지 않은 상태.

```
현재: Client → WebSocket → SignalingHub (raw relay) → Client
의도: Client → WebSocket → SessionManager → MediaProcessor → STT → AgentOrchestrator → Client
```

### 2.2 인증 후 사용자 ID 미연결

`_authenticate_ws()`가 `True/False`만 반환하고 사용자 정보를 버림. 클라이언트가 `sender_id`를 임의 조작하여 사용자 사칭 가능.

```python
# 현재 - user 정보 소실
if not await _authenticate_ws(websocket):
    return

# 개선 - user_id 바인딩 필요
user = await _authenticate_ws(websocket)
if not user:
    return
```

### 2.3 Room 접근 권한 검증 없음

유효한 토큰만 있으면 아무 `room_id`에 참여 가능 → 도청 위험.

### 2.4 DB 세션 누수

```python
async for db in get_async_db():
    await verify_token_from_db(token, db)
    return True  # generator cleanup 미보장
```

### 2.5 SignalingHub 동기화 없음

`join`/`leave`/`relay` 간 `asyncio.Lock` 미사용 → 동시 호출 시 `Set changed size during iteration` 에러 가능.

---

## 3. 구조적 문제 (P1)

### 3.1 Agent 결과 클라이언트 미전달

```
Audio → MediaProcessor → STT(mock) → AgentOrchestrator → 로그 출력 (끝)
```

`_process_final_agent_output`이 blocker/insight를 로그로만 출력. WebSocket push 경로 없음.

### 3.2 SessionManager 글로벌 Lock 병목

모든 방이 단일 `asyncio.Lock`을 공유하며, lock 내에서 `send_text()` (네트워크 I/O) 수행 → 방 단위 lock으로 변경 필요.

### 3.3 Heartbeat 없음

좀비 연결 감지 불가. 주기적 ping/pong 필요.

### 3.4 메시지 제한 없음

메시지 크기 제한, rate limiting 없음 → DoS 취약.

---

## 4. 확장성 제한 (P2)

### 4.1 인메모리 단일 인스턴스

`SignalingHub`, `HuddleSessionManager` 모두 인메모리 dict 기반. 다중 서버 인스턴스 시 같은 방 참가자가 다른 인스턴스에 연결되면 시그널링 불가.

**해결**: Redis Pub/Sub 기반 cross-instance broadcast (프로젝트에 Redis 의존성 이미 존재).

### 4.2 aiortc 서버측 WebRTC CPU 부하

참가자당 `RTCPeerConnection`을 서버에서 생성 → CPU 집약적. STT만 필요하다면 클라이언트 `MediaRecorder` + WebSocket 청크 전송이 훨씬 경량.

### 4.3 AgentOrchestrator 동시성 제한

Room당 단일 `current_task`만 허용, 새 요청 시 이전 작업 취소. 3초마다 STT 결과가 들어오면 대부분의 agent 실행이 완료되지 못함.

### 4.4 오디오 버퍼링

- VAD(Voice Activity Detection) 없음 → 무음 구간도 처리
- STT 결과 간 문맥 연결 없음 → 문장이 3초 경계에서 잘림
- `_execute_stt`가 mock만 반환

---

## 5. 누락 기능

### Huddle (Google Meet-like)

| 기능                    | 상태                                     |
| ----------------------- | ---------------------------------------- |
| 참가자 목록 / Presence  | 없음                                     |
| 화면 공유 시그널링      | 없음                                     |
| 미디어 제어 (mute 전파) | 스키마에만 정의 (`SystemControlMessage`) |
| 녹화                    | 없음                                     |
| 방 생성/관리 REST API   | 없음                                     |
| 실제 STT 연동           | mock만 존재                              |
| Agent 결과 push         | 없음                                     |
| Heartbeat / Ping-Pong   | 없음                                     |
| 재연결 처리             | 없음                                     |
| 참가자 수 제한          | 없음                                     |

### DM (Slack DM-like)

전혀 미구현. 필요 컴포넌트:

- **도메인 모듈**: `server/src/app/dm/` (model, schemas, service, api)
- **DB 테이블**: `dm_conversations`, `dm_messages`, `dm_participants`, `dm_read_receipts`
- **WebSocket 엔드포인트**: `/ws/dm` - 인증, 연결 관리, 메시지 라우팅
- **ConnectionManager**: user_id → WebSocket 매핑, 온라인 상태 추적
- **기능**: 1:1/그룹 DM, 메시지 히스토리, 읽음 표시, 타이핑 인디케이터, 파일 첨부, 수정/삭제, 멘션, 검색, Presence

---

## 6. 코드 품질

| 문제                                                                           | 위치                                       |
| ------------------------------------------------------------------------------ | ------------------------------------------ |
| f-string 로깅 (`logger.info(f"...")`) → lazy formatting 필요                   | `session_manager.py`, `media_processor.py` |
| CLI 코드에서 `OfferMessage(sdp=...)` 호출 시 `sender_id` 누락 → Pydantic 에러  | `initiator.py`                             |
| `media_processor.stop()`에서 `_stt_tasks` 미취소                               | `media_processor.py`                       |
| `SignalingHub`의 connection 타입이 `object` → `Protocol` 또는 제네릭 활용 필요 | `hub.py`                                   |
| standalone 서버 무인증                                                         | `signal.py`                                |

---

## 7. 권장 작업 순서

### P0 - 즉시 수정 (보안/버그)

1. `_authenticate_ws` → user_id 반환 + sender_id 서버측 주입
2. Room 접근 권한 검증 추가
3. DB 세션 누수 수정 (`contextlib.aclosing` 또는 `anext()`)
4. `SignalingHub`에 `asyncio.Lock` 추가

### P1 - 단기 개선 (기능 연결)

5. 아키텍처 결정: 서버측 WebRTC(aiortc) vs 클라이언트 MediaRecorder 방식
6. Dead code 연결 또는 재설계
7. Agent 결과 → WebSocket push 경로 구축
8. Heartbeat 구현
9. 메시지 크기 제한 + Rate limiting

### P2 - 중기 개선 (확장성)

10. Redis Pub/Sub 기반 multi-instance 지원
11. 실제 STT 연동 (Whisper / Google STT) + VAD 도입
12. Presence 시스템

### P3 - 장기 과제 (신규 기능)

13. DM 도메인 모듈 설계 및 구현
14. Huddle + DM 통합 ConnectionManager 설계
15. Prometheus 메트릭 (활성 연결 수, latency p99 등)
