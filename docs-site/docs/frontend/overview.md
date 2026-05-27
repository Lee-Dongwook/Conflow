---
sidebar_position: 1
title: 프론트엔드 가이드
description: Vite + React 18 + Tailwind CSS 4 프론트엔드 아키텍처
---

# 프론트엔드 가이드

Conflow의 프론트엔드는 **Vite 8 + React 18 + Tailwind CSS 4 + TypeScript 5.7**로 구축되었습니다. 모노레포의 `apps/web/` 디렉터리에 위치합니다.

## 프로젝트 구조

```
apps/web/
├── src/
│   ├── pages/          # 페이지 컴포넌트
│   ├── widgets/        # 위젯 (복합 UI 블록)
│   ├── data/           # 목 데이터, 상수
│   ├── App.tsx         # 루트 컴포넌트
│   ├── main.tsx        # 엔트리포인트
│   └── vite-env.d.ts   # Vite 타입 선언
├── index.html
├── styles.css          # 글로벌 스타일 (Tailwind 포함)
├── vite.config.ts      # Vite 설정
├── tsconfig.json       # TypeScript 설정
└── package.json
```

## 의존성 패키지

프론트엔드는 모노레포의 내부 패키지를 사용합니다:

### packages/core
공유 인프라 패키지:
- **Axios 클라이언트**: 백엔드 API 통신을 위한 설정된 HTTP 클라이언트
- **Zod 스키마**: API 응답 및 외부 데이터 검증
- **Utils**: 날짜 포맷, 문자열 처리 등 유틸리티

### packages/ui
Atomic Design 기반 React 컴포넌트:
- Button, Card, Avatar 등 기본 컴포넌트
- 일관된 디자인 시스템
- Tailwind CSS 스타일링

## 코딩 표준

### Immutability
```typescript
// 올바른 사용
const items = data.map((item) => ({ ...item, processed: true }));
const filtered = items.filter((item) => item.active);

// 금지: let 사용
// let count = 0;  // 사용 금지
```

### No `any`
```typescript
// 올바른 사용
const handleResponse = (data: unknown): UserProfile => {
  return userProfileSchema.parse(data);
};

// 금지: any 타입
// const handleResponse = (data: any) => data;  // 사용 금지
```

### Zod 검증
모든 외부 데이터(API 응답, AI 출력)는 반드시 Zod로 검증합니다:

```typescript
import { z } from "zod";

const MeetingSummarySchema = z.object({
  overview: z.string(),
  bullets: z.array(z.string()),
  decisions: z.array(z.string()),
  actions: z.array(z.object({
    assignee: z.string(),
    task: z.string(),
    deadline: z.string().optional(),
  })),
  nextSteps: z.array(z.string()),
});

type MeetingSummary = z.infer<typeof MeetingSummarySchema>;
```

### A2UI-Ready 설계
비즈니스 로직은 React 생명주기와 분리합니다:

```typescript
// 비즈니스 로직은 순수 함수로 작성
const processMeetingData = (raw: unknown): MeetingSummary => {
  const validated = MeetingSummarySchema.parse(raw);
  return {
    ...validated,
    actions: validated.actions.sort((a, b) =>
      a.assignee.localeCompare(b.assignee)
    ),
  };
};

// React 컴포넌트는 UI만 담당
const MeetingSummaryView = ({ data }: { data: MeetingSummary }) => {
  // 렌더링 로직만
};
```

## 개발 명령어

```bash
# 개발 서버 실행 (포트 3000)
pnpm --filter @conflow/web dev

# 프로덕션 빌드
pnpm --filter @conflow/web build

# 타입 체크
pnpm --filter @conflow/web typecheck
```

## 환경 변수

Vite의 환경 변수 규칙에 따라 `VITE_` 접두사를 사용합니다:

```bash
VITE_API_URL=http://localhost:8000
```

## 스타일링

Tailwind CSS 4를 사용하며, `styles.css`에서 글로벌 설정을 관리합니다. `packages/ui` 컴포넌트는 Tailwind 클래스를 사용하여 일관된 디자인 시스템을 유지합니다.
