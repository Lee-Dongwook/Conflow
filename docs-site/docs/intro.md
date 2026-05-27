---
sidebar_position: 1
title: Conflow 소개
description: AI 기반 IT 협업 플랫폼 Conflow의 공식 문서
slug: /intro
---

# Conflow

Conflow는 대학 스터디 팀을 위한 **AI 기반 IT 협업 플랫폼**입니다. 회의 요약, 블로커 감지, 스프린트 관리 등의 핵심 기능을 제공하며, **A2UI-Ready (AI-to-UI)** 아키텍처를 통해 비즈니스 로직을 AI 에이전트가 직접 호출할 수 있도록 설계되었습니다.

## 해결하는 문제

대학 스터디 팀은 협업 과정에서 다음과 같은 어려움을 겪습니다:

| 문제                      | Conflow의 해결 방식                                                        |
| ------------------------- | -------------------------------------------------------------------------- |
| **병목 현상 및 무임승차** | 회의/채팅에서 Blocker와 담당 공백을 자동 추출하여 알림 및 보드 후보로 제안 |
| **마감 기한 망각**        | 논의에서 도출된 마감과 다음 단계를 구조화하여 인박스에 반영                |
| **도구 피로도**           | Notion 대신 AI 회의록 (한 줄 요약 + 액션 리스트) 제공                      |

## 핵심 기능

### AI 회의 요약

Huddle 음성 회의 종료 후, 전사(transcription) 텍스트를 자동으로 구조화된 회의록으로 변환합니다. Overview, 주요 결정사항, 액션 아이템, 다음 단계가 포함됩니다.

### Multi-Agent 시스템

LangGraph 기반의 supervisor가 전문 worker 에이전트들을 오케스트레이션합니다:

- **meeting_summary**: 회의록 요약
- **blocker_triage**: 블로커 감지 및 분류
- **retro_insights**: 회고 인사이트 생성
- **file_analysis**: 파일/문서 분석

### 스프린트 관리

백로그, 칸반 보드, 인박스, 주간 마일스톤 등 애자일 위젯을 통해 팀의 스프린트를 체계적으로 관리합니다.

## 기술 스택

- **Frontend**: Vite 8, React 18, Tailwind CSS 4, TypeScript 5.7
- **Backend**: FastAPI, SQLAlchemy 2 (async), PostgreSQL 16 + pgvector
- **AI/Agents**: LangGraph, LangChain, OpenAI (gpt-4o-mini)
- **Infra**: Docker Compose, uv (Python), pnpm 9 + Turborepo, Redis

## 다음 단계

- [설치 가이드](/docs/getting-started/installation)로 개발 환경을 구성하세요.
- [아키텍처 개요](/docs/architecture/overview)에서 시스템 구조를 파악하세요.
- [Multi-Agent 시스템](/docs/agents/overview)에서 AI 에이전트의 동작 방식을 알아보세요.
