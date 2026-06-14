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

### Task 1. 카피라이팅 (EN)

| 항목                  | 제약                                                       | 산출물       |
| --------------------- | ---------------------------------------------------------- | ------------ |
| Tagline               | ≤60 chars, outcome-focused                                 | 3안          |
| Description           | ≤260 chars, problem→solution                               | 1안          |
| Maker's First Comment | Problem → Multi-Agent/Monorepo solution → MVP feedback ask | 구조화된 1안 |

작성 각도: _"Open Conflow → your team's week is already on screen"_ — Dashboard-as-entry 메시지를 카피에 녹인다.

### Task 2. 시각 자산 명세

| 자산                                | 사양                                             | 비고                         |
| ----------------------------------- | ------------------------------------------------ | ---------------------------- |
| Thumbnail GIF                       | 240×240, 4:3, Multi-Agent workflow               | 프레임별 스토리보드 문서     |
| Gallery Slide 1 (Hero)              | DashboardPage 데모 스크린샷 + 헤드라인           | 코드 자산 재활용             |
| Gallery Slide 2 (Core Workflow)     | MeetingSummaryPage 또는 BoardPage 스크린샷       | 코드 자산 재활용 가능성 점검 |
| Gallery Slide 3 (Tech/Architecture) | LangGraph + Monorepo 다이어그램                  | 신규 제작                    |
| Gallery Slide 4 (Outcome)           | MetricsPage / RetroPage 스크린샷 + 수치 오버레이 | 코드 자산 재활용             |
| Gallery Slide 5 (CTA)               | 로고 + URL + QR + Try Conflow 문구               | 신규 제작 (단순)             |
| OG Image                            | 1200×630, Dashboard 스크린샷 + 로고 합성         | 신규 제작 (단순)             |

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

| 순위 | 작업                                                                   | 산출물                      |
| ---- | ---------------------------------------------------------------------- | --------------------------- |
| 🟢 1 | `widgets/product-hunt-banner` 구현 + `App.tsx` 마운트 + dismiss 영속화 | 코드 + Playwright smoke 1개 |
| 🟢 1 | i18n 키 추가 (`marketing.banner.*`) — en/ko                            | locale JSON                 |
| 🟡 2 | Tagline / Description / Maker's First Comment 작성                     | 카피 마크다운               |
| 🟠 3 | Gallery 5슬라이드 명세 (레이아웃·카피·UI 하이라이트)                   | 슬라이드 스펙 문서          |
| 🟠 3 | Thumbnail GIF 스토리보드 (프레임별)                                    | 스토리보드 문서             |
| 🔵 4 | OG 이미지 + 메타 태그 (`apps/web/index.html`)                          | HTML + 이미지               |
| 🔵 4 | UTM 추적 (`?ref=producthunt`) — 게스트 오버레이 클릭 로깅 (옵션)       | 코드                        |

---

## 4. 사전 결정 필요 (블로커)

1. **Product Hunt 페이지 URL** — Secondary CTA 타깃 (`VITE_PRODUCT_HUNT_URL` 환경변수로 분리)
2. **런칭 D-day** — 자산 마감일 역산용
3. **배너 카피 언어 범위** — EN-only(글로벌 트래픽) vs ko/en 둘 다(i18n 일관성)

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
