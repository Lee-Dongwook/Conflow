# Product Hunt Launch Plan — Conflow

## 0. 문서 목적

Conflow 의 Product Hunt 런칭을 위해 필요한 산출물(카피·시각자산·컴포넌트)과 작업 순서를 정리한다. 본 문서는 i18n 구현이 끝났다는 전제에서 시작한다.

---

## 1. 진입 구조 재해석 (가장 중요)

별도의 랜딩 페이지를 만들지 않는다. 현재 앱 구조상 **Dashboard 가 곧 진입점**이며, PH 방문자는 자연스럽게 다음 흐름을 따른다.

```
PH 방문자(비로그인)
    ↓
DashboardPage (DEMO 데이터로 렌더)
    ↓
게스트 오버레이(z-40) 클릭 가로채기
    ↓
LoginModal
```

이 사실로부터 파생되는 결정들:

- **랜딩 페이지 신규 생성 불필요** — Dashboard 자체가 마케팅 표면이다.
- **PH 배너는 게스트 오버레이보다 위(z-50+)** 에 떠야 클릭이 가능하다.
- **Primary CTA = LoginModal 오픈** 이 외부 PH 페이지 이동보다 전환 효율이 높다.
- **Gallery Slide 1 (Hero) = 실제 Dashboard 데모 스크린샷** 그대로 사용 가능 → 별도 목업 제작 비용 절감.

---

## 2. 산출물 정의 (Skill 기준 재정렬)

### Task 1. 카피라이팅 (EN) — ✅ 작성 완료

> All copy in English. All counts are characters including spaces.
> Writing angle: **Dashboard-as-entry** — _open the app → your team's week is already on screen_.

#### 1-A. Tagline (3 options, ≤60 chars, outcome-focused)

3가지 다른 각도로 작성 — A/B 테스트용.

**Option A — Instant-clarity (50 chars)**

> **See your team's week the moment you open the app.**

- Outcome: zero ramp-up time
- Best if PH audience values "no setup required"

**Option B — Automation (54 chars)**

> **AI agents that watch the standup so you don't have to.**

- Outcome: less coordination tax
- Best for "I'm tired of running meetings" pain

**Option C — Risk-reduction (45 chars)**

> **Catch blockers before they catch your sprint.**

- Outcome: prevent sprint slip
- Best for sprint-savvy / dev-leaning audience

**추천**: PH 리스팅엔 **Option A** — dashboard-as-entry 약속을 가장 즉시 전달하고 머릿속 스크린샷이 쉬움. B/C 는 소셜·이메일 후속용으로 보유.

#### 1-B. Description (≤260 chars, problem → solution)

> **Student teams waste hours stitching Slack, Notion, and Discord. Conflow opens to a live dashboard of your team's week — AI agents summarize meetings, surface blockers, and run sprint logistics so you focus on shipping, not coordinating.**

- 길이: **234 / 260**
- 구조: Problem(3 tools, scattered) → Solution(single live dashboard) → Outcome(focus on shipping)
- PH 검색 키워드: AI agents, sprint, meetings, blockers, dashboard

#### 1-C. Maker's First Comment

구조: Problem(체험담) → How Conflow solves it(Multi-Agent + Monorepo) → 솔직한 피드백 요청. 보도자료가 아닌 메이커가 이야기 풀어내는 톤.

```
Hey Product Hunt,

I built Conflow because running a university study team turned out to be a
coordination tax. We had Slack for chat, Notion for docs, Discord for huddles —
and every Sunday someone still asked "wait, what's due Monday?". Meeting notes
lived in three places, blockers surfaced too late, and the sprint plan was
already obsolete by Wednesday.

Conflow flips the entry point. The moment you open the app, your team's week
is already on screen — current sprint goal, who owns what, what's blocked,
what's next. No setup wizard, no empty state.

Under the hood, a LangGraph multi-agent supervisor routes work to specialized
workers: meeting summary, blocker triage, retro insights, sprint planning.
The whole codebase is a pnpm + Turbo monorepo with an A2UI-ready architecture —
every business function is a headless, schema-first module the agents can
invoke directly. That means new agent capabilities ship without rewriting the
UI, and the UI itself stays thin and replaceable.

This is genuinely an MVP. The rough edges are real, and I'd love brutally
honest feedback:

  1. Does the dashboard-as-entry feel like clarity or chaos on first open?
  2. Where does the AI summary fall short of what your team would actually use?
  3. What is the one missing surface that would make Conflow replace your
     current stack — and what is the one feature you would not pay attention
     to even if we built it?

Reply here or DM me. I will read every word. Thank you for hunting with us.

— Dongwook, maker of Conflow
```

- 길이: ~1,500 chars (PH first comment 권장: 1,000–2,000)
- 3 단락 컨텍스트 + 3 번호 질문 = 스캔 가능
- **부정 시그널 유도** ("feature you would not pay attention to") — 일반적인 "what do you think?" 보다 날카로운 피드백을 받음

#### 1-D. 부록 — 소셜 배포 카피

**Twitter / X (≤280 chars)**

> Today we're launching Conflow on Product Hunt.
>
> The pitch in one line: open the app, your team's week is already on screen.
>
> AI agents summarize meetings, surface blockers, and run sprint logistics — so you ship the project, not the coordination.
>
> Link → [PH URL]

**LinkedIn (short)**

> Most coordination tools start with an empty workspace. Conflow starts with your team's week already on screen.
>
> We launched on Product Hunt today. Would love honest feedback from anyone who has run a study team, a side project, or a small squad and felt the standup-vs-shipping tradeoff.
>
> Link → [PH URL]

**배너 i18n 소스 (이미 구현됨)**

- `marketing.banner.title` — Welcome, Product Hunters!
- `marketing.banner.subtitle` — Conflow is live on Product Hunt — open the app and your team's week is already on screen.
- `marketing.banner.ctaPrimary` — Try Conflow free
- `marketing.banner.ctaSecondary` — Upvote on Product Hunt

### Task 2. 시각 자산 명세 — 📐 명세 작성 완료 / 제작 대기

> 모든 슬라이드는 **Inter / SF Pro** 계열 sans-serif, 본문 그레이 `#0F172A` (slate-900), 강조 오렌지 `#F97316` (PH 컬러 매칭) 기준. 픽셀 단위 사양은 Pencil/Figma 작업 시 시작값.

#### 자산 개요

| 자산                                | 사양                              | 제작 방식                               | 비고                                                  |
| ----------------------------------- | --------------------------------- | --------------------------------------- | ----------------------------------------------------- |
| Thumbnail GIF                       | **240×240** (1:1), ≤3MB, 5초 루프 | React+Framer Motion → 화면녹화 → Gifski | Skill 문서엔 "4:3" 이라 적혀있으나 PH 현행 스펙은 1:1 |
| Gallery Slide 1 (Hero)              | 1270×760, 16:9 근사               | Dashboard 스크린샷 + 텍스트 오버레이    | 코드 자산 재활용                                      |
| Gallery Slide 2 (Core Workflow)     | 1270×760                          | MeetingSummaryPage 스크린샷 + 캡션      | 코드 자산 재활용                                      |
| Gallery Slide 3 (Tech/Architecture) | 1270×760                          | Excalidraw 또는 Pencil 신규 다이어그램  | 신규 제작                                             |
| Gallery Slide 4 (Outcome)           | 1270×760                          | MetricsPage 스크린샷 + 숫자 오버레이    | 코드 자산 재활용                                      |
| Gallery Slide 5 (CTA)               | 1270×760                          | 로고 + QR + 문구                        | 신규 제작 (단순)                                      |
| OG Image                            | 1200×630                          | Dashboard 스크린샷 + 로고 합성          | 신규 제작 (단순)                                      |

---

#### 2-A. Thumbnail GIF — 프레임별 스토리보드

**컨셉**: Multi-Agent 가 회의 종료 신호를 받아 → 분산 처리 → Dashboard 타일이 살아나는 한 사이클.

**기술 사양**

- 캔버스: 240×240 (1:1, PH 현행 스펙)
- 길이: **5초**, **24 fps**, 무한 루프
- 색감: 화이트 베이스 + 오렌지(#F97316) 강조, 다크 노드(slate-800)
- 출력: GIF ≤3MB. 코드 기반 캡처(ScreenStudio) → Gifski 압축

**프레임 시퀀스**

| 시점 | 프레임    | 화면 구성                                                                            | 모션                          |
| ---- | --------- | ------------------------------------------------------------------------------------ | ----------------------------- |
| 0.0s | F1 (정지) | 중앙에 `Conflow` 로고, 하단에 4개 회색 노드 (`Summary` `Blocker` `Retro` `Planning`) | Idle pulse                    |
| 0.5s | F2        | 좌측 상단에 `Meeting ended` 칩 등장 → 중앙 `Supervisor` 노드로 화살표                | 칩이 supervisor 로 빨려들어감 |
| 1.5s | F3        | Supervisor → `Summary` 노드 라우팅, 노드 오렌지로 점등                               | 화살표 stroke 애니메이션      |
| 2.5s | F4        | Summary 진행 중에 `Blocker Triage` 도 병렬 점등                                      | 두 노드 동시 발광             |
| 3.5s | F5        | 두 노드 결과가 상단 Dashboard 타일로 수렴 (`+3 actions`, `1 blocker`)                | 결과가 타일에 plug-in         |
| 4.5s | F6        | Dashboard 타일이 풀 컬러로 전환, "Your team's week" 캐치 등장                        | 타일 풀스크린 확대            |
| 5.0s | → F1      | 페이드 후 다시 F1                                                                    | 루프                          |

**구현 가이드**

- React 컴포넌트로 작성 (`apps/web/src/widgets/ph-thumbnail-demo/` 임시 위치) → ScreenStudio 로 영역 캡처 → Gifski 로 압축
- Framer Motion `animate` + `staggerChildren` 으로 노드 등장
- 텍스트는 SVG `text` 로 — 안티앨리어싱이 GIF 압축에 강함

---

#### 2-B. Gallery Slide 1 — Hero (실 Dashboard 스크린샷)

**목적**: 첫인상에서 _"앱 열면 팀의 한 주가 이미 화면에 있다"_ 메시지를 0초 컷.

**레이아웃 (1270×760)**

```
+--------------------------------------------------+
|  [Logo·Conflow]              [Live on PH 배지]   |  ← top 60px
|                                                  |
|  Your team's week — already on screen.           |  ← H1 (48pt, slate-900)
|  Open Conflow, skip the standup.                 |  ← sub (20pt, slate-500)
|                                                  |
|  +--------- Dashboard 스크린샷 ---------+        |  ← 실 캡처 (1100×540)
|  |  TeamName · Sprint 3 · Mar 10–23   |          |     drop shadow + radius 16
|  |  Weekly goal: ...                  |          |
|  |  [Deadline] [Progress 62%]         |          |
|  |  [Task list with avatars]          |          |
|  +------------------------------------+          |
+--------------------------------------------------+
```

**카피**

- H1: `Your team's week — already on screen.`
- Sub: `Open Conflow, skip the standup.`
- 우상단 배지: `Live on Product Hunt 🟠` (이모지는 실제 PH 로고 SVG 로 교체)

**하이라이트 처리**

- Dashboard 의 **Progress 62%** 와 **Weekly goal** 두 카드만 살짝 spotlight (다른 영역은 6% 어두운 오버레이)

---

#### 2-C. Gallery Slide 2 — Core Workflow (MeetingSummaryPage)

**목적**: Multi-Agent 가 실제로 _무엇을_ 자동화하는지 한눈에.

**레이아웃**

```
+--------------------------------------------------+
|  Less standup, more shipped sprints.             |  ← H1 (40pt)
|                                                  |
|  Step 1     →     Step 2     →     Step 3        |  ← 3-step 헤더
|  Huddle           AI Summary       Actions       |     (각 스텝당 1줄 부제)
|  ends             generated        synced        |
|                                                  |
|  +------- MeetingSummaryPage 스크린샷 -------+  |
|  |  [Transcript pane] | [Summary pane]       |  |
|  |                    | [Action items]       |  |
|  +------------------------------------------+  |
+--------------------------------------------------+
```

**카피**

- H1: `Less standup, more shipped sprints.`
- Step 1: `Huddle ends`
- Step 2: `AI Summary generated`
- Step 3: `Actions synced to board`

**하이라이트**

- 스크린샷 내 **Action items 패널**에 펄스 링 효과 (PNG 후처리)

---

#### 2-D. Gallery Slide 3 — Tech / Architecture (신규 다이어그램)

**목적**: 개발자 PH 청중에게 _"진짜 멀티에이전트 + 모노레포"_ 임을 시각화.

**레이아웃**

```
+--------------------------------------------------+
|  A multi-agent backend. A monorepo you can read. |  ← H1
|                                                  |
|  +-------- 다이어그램 (수동 작성) --------+      |
|  |                                          |    |
|  |   [Supervisor]                           |    |
|  |       ↓                                  |    |
|  |   ┌───┴───────────────┐                  |    |
|  |   │ Summary  Blocker  │ ← 4개 워커 노드   |    |
|  |   │ Retro    Planning │                  |    |
|  |   └───┬───────────────┘                  |    |
|  |       ↓                                  |    |
|  |   [A2UI Headless Modules]                |    |
|  |       ↓                                  |    |
|  |   [React UI · pnpm + Turbo monorepo]     |    |
|  +------------------------------------------+    |
|                                                  |
|  LangGraph · FastAPI · Vite · Tailwind · pgvector |  ← 기술 스택 chip 줄
+--------------------------------------------------+
```

**카피**

- H1: `A multi-agent backend. A monorepo you can read.`
- 하단 스택 chips: `LangGraph` `FastAPI` `Vite + React 18` `Tailwind 4` `pgvector` `Supabase`

**제작 도구 후보**: Excalidraw (손그림 톤, 신뢰감) **또는** Pencil MCP (.pen 파일로 브랜드 색감 정확 매칭). 추천: **Excalidraw** — 개발자 신뢰 톤이 PH 청중과 잘 맞음.

---

#### 2-E. Gallery Slide 4 — Built for student teams (시나리오 슬라이드)

> ✅ **결정**: 베타 실측 데이터 부재. 수치형 Outcome 슬라이드 대신 **사용 시나리오** 슬라이드로 진행. 베타 데이터 확보 시 추후 교체.

**목적**: _"우리 팀 같은 곳에서 쓰는구나"_ 의 자기 동일시. 페르소나·시나리오 톤.

**레이아웃 (1270×760)**

```
+--------------------------------------------------+
|  Built for the teams nobody built for.           |  ← H1 (40pt)
|                                                  |
|  +-- 3 columns of persona cards --+              |
|  |  🎓 Capstone teams              |             |
|  |     "5 majors, 1 deadline."     |             |
|  |     [task list mini preview]    |             |
|  |---------------------------------|             |
|  |  📚 Study groups                |             |
|  |     "Weekly KPT, no chaos."     |             |
|  |     [retro snippet]             |             |
|  |---------------------------------|             |
|  |  💻 Side-project squads         |             |
|  |     "Async standups that ship." |             |
|  |     [board snippet]             |             |
|  +---------------------------------+             |
+--------------------------------------------------+
```

**카피**

- H1: `Built for the teams nobody built for.`
- 3개 페르소나 카드:
  - **Capstone teams** — _"5 majors, 1 deadline."_
  - **Study groups** — _"Weekly KPT, no chaos."_
  - **Side-project squads** — _"Async standups that ship."_

**하이라이트**: 각 카드 안에 실제 페이지(BoardPage / RetroPage / DashboardPage)의 작은 스니펫 캡처를 넣어 _제품 진짜 있다_ 시그널 유지.

> 📌 **베타 데이터 확보 시 교체 안**: H1 → `What teams ship after switching to Conflow.` / 3개 숫자(예: `-45% standup time`, `3 hours saved / week`, `100% blocker visibility`) + 자가보고 footnote. 이 노트는 데이터 확정 후 다시 활성화.

---

#### 2-F. Gallery Slide 5 — CTA

**목적**: 마지막 슬라이드는 **단순할수록 강함**. 1초 안에 행동 유도.

**레이아웃**

```
+--------------------------------------------------+
|                                                  |
|             [Conflow 로고 — 큼]                  |
|                                                  |
|       Try Conflow free → conflow.app             |  ← 48pt
|                                                  |
|       [QR 코드 240×240]                          |  ← 우측 또는 중앙 하단
|                                                  |
|       Upvote us on Product Hunt today            |  ← 18pt, 오렌지
|                                                  |
+--------------------------------------------------+
```

**카피**

- 메인 CTA: `Try Conflow free → conflow.app`
- 보조: `Upvote us on Product Hunt today`
- QR 타겟: PH 페이지 URL (확정 후 생성)

---

#### 2-G. OG Image (1200×630)

소셜 공유용. 갤러리 Slide 1 의 압축 버전과 동일 컨셉.

**레이아웃**

```
+--------------------------------------------------+
|  [Conflow logo]            Live on Product Hunt  |
|                                                  |
|  Your team's week — already on screen.           |
|                                                  |
|  +-- Dashboard 스크린샷 (좌측 정렬, 60%) --+    |
|  |                                          |    |
|  +------------------------------------------+    |
+--------------------------------------------------+
```

**카피**: Slide 1 과 동일 H1. 부제는 생략 (1200×630 가독성 우선).

**현재 상태** (`apps/web/index.html` 점검 결과)

- ✅ OG / Twitter / JSON-LD 메타태그 **이미 완비** (`og:title`, `og:description`, `og:image=/og-image.png`, `og:locale=ko_KR`)
- ✅ `og:locale:alternate=en_US` 추가 완료 (PH 글로벌 청중 대응)
- ❌ **실제 이미지 파일 `apps/web/public/og-image.png` 미존재** — 신규 제작 필요
- ❌ `favicon.svg`, `apple-touch-icon.png` 도 미존재 (별도 작업)

**제작 시 주의**

- 파일 경로는 기존 메타와 일치시키기 — `apps/web/public/og-image.png` (서브폴더 X)
- 한·영 버전 분기 X — Korean OG primary 로 유지하고 description 은 키워드 위주라 영문 청중도 의미 전달 가능. 따로 EN 변형 만들면 캐시 무효화·SEO 분산 위험.

---

#### 2-H. 제작 핸드오프 체크리스트

- [ ] Slide 1·2·4 의 **실 스크린샷 수집** — DashboardPage / MeetingSummaryPage / MetricsPage 데모 모드로 캡처 (Retina 2x)
- [ ] Slide 3 다이어그램 — Excalidraw 초안 → 브랜드 색 톤 정리 → PNG export
- [ ] Slide 5 — QR 코드는 PH URL 확정 후 생성 (qrcode-svg 사용 가능)
- [ ] Thumbnail GIF — `widgets/ph-thumbnail-demo/` 임시 React 컴포넌트 작성 → ScreenStudio 캡처
- [ ] OG 이미지 → `apps/web/public/og-image.png` 저장 (기존 `index.html` 메타가 이 경로 참조)
- [ ] 모든 자산 sRGB 컬러스페이스, GIF/PNG 압축 후 최종 사이즈 확인 (PH 갤러리 슬라이드 ≤ 2MB 권장)

### Task 3. `ProductHuntBanner` 컴포넌트

- **위치**: `widgets/product-hunt-banner/` (마케팅 컨텍스트 + dismiss state 합성이므로 `shared/ui` 의 atomic 원칙과 다름)
- **마운트 지점**: `apps/web/src/app/App.tsx` `AppContent` outer wrapper 최상단
- **노출 조건**: `session.status === 'unauthenticated'` AND `localStorage['ph-banner-dismissed-v1']` 미설정
- **CTA 2개**:
  - Primary: **Try Conflow free** → `onLoginRequest()` (LoginModal 오픈)
  - Secondary: **Upvote on Product Hunt ↗** → 외부 링크 (`rel="noopener noreferrer"`)
- **접근성**: `role="banner"`, dismiss 버튼 `aria-label`, ESC 키 dismiss, sticky top

마운트 위치 의사 코드 (`let` 금지):

```tsx
return (
  <>
    <ProductHuntBanner
      onLoginRequest={() => setLoginOpen(true)}
      productHuntUrl={import.meta.env.VITE_PRODUCT_HUNT_URL}
    />
    <div className="relative flex min-h-screen bg-slate-50">
      {isGuest && <div className="absolute inset-0 z-40 ..." />}
      <SideBar ... />
      <div className="flex min-w-0 flex-1 flex-col">...</div>
    </div>
    <LoginModal open={loginOpen} onClose={() => setLoginOpen(false)} />
  </>
)
```

i18n 키 신설: `marketing.banner.title`, `marketing.banner.subtitle`, `marketing.banner.ctaPrimary`, `marketing.banner.ctaSecondary` (`en`, `ko` 둘 다).

> **주의**: Skill 문서에 "Next.js 16 + Tailwind v4" 라고 적혀 있으나 실제 스택은 **Vite 8 + React 18 + Tailwind 4** 이다. Server Component 가 아닌 일반 Client Component 로 구현한다.

---

## 3. 우선순위 To-Do

| 순위    | 작업                                                                     | 산출물                       |
| ------- | ------------------------------------------------------------------------ | ---------------------------- |
| ✅ 완료 | `widgets/product-hunt-banner` 구현 + 마운트 + dismiss 영속화             | 코드 (Playwright smoke 보류) |
| ✅ 완료 | i18n 키 (`marketing.banner.*`) — en/ko                                   | locale JSON                  |
| ✅ 완료 | Tagline / Description / Maker's First Comment                            | Task 1 인라인                |
| ✅ 완료 | Gallery 5슬라이드 명세                                                   | Task 2 인라인                |
| ✅ 완료 | Thumbnail GIF 스토리보드                                                 | Task 2-A                     |
| ✅ 완료 | 메타태그 + `og:locale:alternate=en_US`                                   | `apps/web/index.html`        |
| ✅ 완료 | UTM 추적 + 게스트 오버레이·배너 CTA 이벤트 로깅                          | `shared/lib/launch-ref.ts`   |
| 🔵 잔여 | OG 이미지 PNG → `apps/web/public/og-image.png`                           | 디자인 작업                  |
| 🔵 잔여 | Slide 1·2·4 스크린샷 + Slide 3 다이어그램 + Slide 5 QR + GIF 렌더        | 캡처/디자인 작업             |
| 🔵 잔여 | analytics provider → `window.addEventListener('conflow:launch', …)` 구독 | 코드 (런칭 후도 가능)        |

---

## 4. 사전 결정 필요 (블로커)

1. **Product Hunt 페이지 URL** — Secondary CTA 타깃 (`VITE_PRODUCT_HUNT_URL` 환경변수로 분리)
2. **런칭 D-day** — 자산 마감일 역산용
3. **배너 카피 언어 범위** — EN-only(글로벌 트래픽) vs ko/en 둘 다(i18n 일관성)
4. **Primary Tagline 확정** — Option A / B / C 중 택 1 (추천: A)
5. **Maker Comment 에 학교·기수 등 사회적 증거 명시 여부** — 신뢰도 ↑ vs 익명성 유지
6. **Korean 배너 톤 native 검수** — 현재 자동 번역 톤이라 원어민 1차 검토 필요

---

## 5. 💡 이미지/GIF 외부 AI 활용 전략 — 솔직한 의견

> _"이미지나 GIF는 외부 AI를 써야 하지 않을까?"_ 에 대한 답.

**결론: 선택적 사용. 핵심 제품 표현물에는 비추, 보조 장식물에는 추천.**

### ✅ 외부 AI 가 유리한 영역

| 자산                          | 도구 후보            | 이유                         |
| ----------------------------- | -------------------- | ---------------------------- |
| 배경 그라데이션·추상 일러스트 | Midjourney, Ideogram | 브랜드 톤만 맞으면 변형 빠름 |
| 데코레이션 아이콘 변형        | DALL-E, Recraft      | 일관 스타일 일괄 생성        |
| 카피용 헤드라인 후보 다양화   | Claude/GPT 텍스트    | 이미 사용 중                 |

### ❌ 외부 AI 가 불리한 영역

| 자산                           | 비추 이유                                                                                               | 권장 대안                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Multi-Agent Workflow GIF       | Runway/Pika/Veo 는 "추상 소프트웨어 워크플로우" 표현 약함. 출력이 SF 느낌이라 제품 신뢰도를 오히려 깎음 | React/SVG/Lottie 로 실제 다이어그램 코딩 → ScreenStudio/Gifski 로 GIF 캡처 |
| 제품 스크린샷류 (Hero·Outcome) | AI 생성 UI 는 uncanny — 가짜 버튼·왜곡된 텍스트로 신뢰 하락                                             | 실제 페이지 스크린샷 + Figma/Pencil 오버레이                               |
| Tech/Architecture 다이어그램   | AI 가 LangGraph/Monorepo 구조를 정확히 표현 못함                                                        | Excalidraw / Mermaid / Pencil 수동 작성                                    |

### 🎯 권장 워크플로우

1. **실 스크린샷 우선** — Slide 1·2·4 는 실제 DashboardPage·MeetingSummaryPage·MetricsPage 캡처로 해결 (제작비 0)
2. **Pencil MCP 활용** — 이 프로젝트에 Pencil MCP 가 이미 연결되어 있다. `.pen` 파일로 Slide 3·5 와 OG 이미지를 디자인하면 코드와 동일한 환경에서 관리 가능
3. **외부 AI 는 보조 장식에만** — 배경, 아이콘, 데코 일러스트 같은 비핵심 영역
4. **GIF 는 코드 기반** — React+Framer Motion 으로 Multi-Agent 흐름 애니메이션 구현 → 화면 녹화 → Gifski 압축. 240×240 사이즈면 파일 크기·정확도 모두 만족

### 추가 도구 후보

- **ScreenStudio / Gifski** — 화면 녹화 → 최적화된 GIF/MP4
- **Rive** — 인터랙티브 애니메이션, GIF 익스포트 가능
- **Excalidraw** — 손그림 느낌 다이어그램, Architecture 슬라이드용
- **Pencil MCP** _(이미 보유)_ — 디자인 파일 통합 관리

---

## 6. 추천 일정 (3일 압축안)

| Day      | 작업                                                           |
| -------- | -------------------------------------------------------------- |
| Day 1 AM | 블로커 3개 결정 → 배너 카피·i18n 키 확정                       |
| Day 1 PM | `widgets/product-hunt-banner` 구현 + 마운트 + Playwright smoke |
| Day 2 AM | Tagline·Description·Maker's First Comment 작성                 |
| Day 2 PM | 갤러리 5슬라이드 명세 작성 + 실 스크린샷 수집                  |
| Day 3 AM | GIF 스토리보드 + 코드 기반 애니메이션 프로토타입               |
| Day 3 PM | OG 이미지 + 메타 태그 + 디자이너(또는 Pencil) 핸드오프         |

---

## 7. Open Questions

- [ ] 배너 dismiss 영속화 키: `localStorage` vs `sessionStorage` (재방문 시 보일지 여부)
- [ ] PH 런칭 후 배너 자동 sunset 일자 — 일주일? 한 달?
- [ ] UTM `?ref=producthunt` 진입 시 배너 강조 vs 그대로 노출
- [ ] Tech Slide 다이어그램에 백엔드 LangGraph 내부 구조 어디까지 공개할지
