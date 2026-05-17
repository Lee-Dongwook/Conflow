# Project Overview

Conflow is a **pnpm + Turbo monorepo** that delivers a Tanstack Start (SSR) front-end to user.
It is a comprehensive IT business solution providing meeting summarization, Gantt chart management, and Agile sprint monitoring, designed with an **A2UI-ready** architecture.

---

## Core Principles

- **Architecture**: Pragmatic Feature-Sliced Design (FSD).
- **Strict Immutability**: Strictly no `let`. Use `const` only. Apply functional programming (`map`, `filter`, `reduce`).
- **Logical Purity**: No emotional filler in comments. Use self-documenting TypeScript types.
- **No Guessing**: State `Unknown` and request the schema if API/Library specs are unclear.
- **SSR First**: Leverage TanStack Start's Server Functions for data mutations and secure API calls.

---

## Monorepo Structure & Dependency Rules

**Flow**: `apps/web` → `packages/business` → `packages/ui` → `packages/core`.

- **packages/core**: Infrastructure only (API Client, SSE Handlers, Date/Chart Utils). **Zero Business Logic, Zero UI**.
- **packages/ui**: Atomic UI components. **Zero Business Logic, Zero API Calls**.
- **packages/business**:
  - **entities/**: Domain data schemas and pure state logic.
  - **features/**: Independent user actions (e.g., `executeSummary`, `calculateGantt`). Must be logic-heavy and UI-agnostic.
- **apps/web (TanStack Start)**:
  - **routes/**: File-based routing and Loaders/Actions.
  - **widgets/**: Complex UI blocks combining multiple features for the Dashboard.

---

## Coding Standards & A2UI Strategy

- **Package Manager**: Strictly `pnpm`.
- **Framework**: TanStack Start. Use `createServerFn` for all server-side operations (DB/External API).
- **A2UI Readiness**:
  - **Headless Logic**: Logic in `features/` must be decoupled from React lifecycle to allow AI Agent invocation.
  - **Schema-First**: Every feature must have a defined Input/Output Schema (Zod) for AI interoperability.
- **State Management**: Use TanStack Query for server state. Avoid direct mutation; use immutable updates only.

---

## Prohibited Practices

- **No Circular Dependencies**: Strict layer isolation.
- **No Direct `let`**: Use `const`.
- **No `any`**: Use `unknown` or strict interfaces.
- **No Layout Shift**: Use TanStack Start `Loaders` for pre-fetching essential dashboard data to ensure stable UX.

---

## Business Logic & Reliability (PM Perspective)

- **Event Tracking**: All actions in `features/` must log `Context` (Feature ID, Runtime, Status).
- **Third-party Abstraction**: Use **Adapter Pattern** in `core/` for external services (Slack, Jira) to prevent vendor lock-in.
- **Validation Layer**: **Zod Mandatory** for AI-generated content and External API responses before reaching `entities/`.
- **Dashboard Resiliency**: Mandatory `Skeleton` for async loading and `Error Boundary` for each widget to prevent full-page crashes.

---

## WorkSpace

Configure Like this

```
conflow/
├── apps/
│   └── web/                        # TanStack Start (SSR Frontend)
│       ├── src/
│       │   ├── routes/             # TanStack Start File-based Routing
│       │   │   ├── __root.tsx      # Root Layout & Global Providers
│       │   │   ├── index.tsx       # Home / Marketing Page
│       │   │   └── dashboard.tsx   # Main Dashboard Page
│       │   ├── widgets/            # Feature combinations (e.g., GanttWidget, SummaryCard)
│       │   ├── app/                # Global Styles & SSR Entry points
│       │   └── main.tsx
│       ├── public/
│       └── package.json
│
├── packages/
│   ├── business/                   # Logic & Domain Layer (FSD: Entities/Features)
│   │   ├── src/
│   │   │   ├── entities/           # Data Schemas (Zod) & Domain States
│   │   │   │   ├── meeting.ts
│   │   │   │   ├── sprint.ts
│   │   │   │   └── gantt.ts
│   │   │   └── features/           # Headless User Actions (A2UI Ready)
│   │   │       ├── use-summary/    # Meeting summary logic
│   │   │       ├── use-gantt/      # Gantt calculation logic
│   │   │       └── use-agile/      # Sprint monitoring logic
│   │   └── package.json
│   │
│   ├── ui/                         # Atomic Design System (Shared UI)
│   │   ├── src/
│   │   │   ├── components/         # Button, Input, Modal, Skeleton
│   │   │   └── index.ts            # Public API for UI components
│   │   └── package.json
│   │
│   └── core/                       # Infrastructure Layer (Shared Utils/Clients)
│       ├── src/
│       │   ├── api/                # Axios/Fetch client & SSE handlers
│       │   ├── adapters/           # Slack/Jira/AI Model adapters
│       │   ├── utils/              # Pure Date/Chart/String utils
│       │   └── constants/          # Global Configs & Constants
│       └── package.json
│
├── turbo.json                      # Turborepo Config
├── pnpm-workspace.yaml             # pnpm Workspace Definition
├── pnpm-lock.yaml
└── package.json

```

## Operational Boundaries

- **Manual Execution Only**: The AI must never execute commands for package installation, testing, or build processes automatically.

- **Guidance Only**: All command-line operations (e.g., pnpm install, pnpm test, turbo build) must be suggested as code blocks for the user to review and execute manually.

- **Responsibility**: The user retains full control over the terminal environment and workspace state changes.

-------

---
description: Python / FastAPI backend conventions for server/
globs: server/**/*
alwaysApply: false
---

# Python Developer

You are an AI assistant specialized in Python development.

Your approach emphasizes:Clear project structure with separate directories for source code, tests, docs, and config.

Modular design with distinct files for models, services, controllers, and utilities.Configuration management using environment variables.

Robust error handling and logging, including context capture.

Comprehensive testing with pytest.

Dependency management via https://github.com/astral-sh/uv and virtual environments.

Code style consistency using Ruff.

CI/CD implementation with GitHub Actions or GitLab CI.

AI-friendly coding practices:You provide code snippets and explanations tailored to these principles, optimizing for clarity and AI-assisted development.

Follow the following rules:For any python file, be sure to ALWAYS add typing annotations to each function or class.

Be sure to include return types when necessary.
Add descriptive docstrings to all python functions and classes as well.

Please use pep257 convention.
Update existing docstrings if need be.

Make sure you keep any comments that exist in a file.When writing tests, make sure that you ONLY use pytest or pytest plugins, do NOT use the unittest module.

All tests should have typing annotations as well. All tests should be in ./tests. Be sure to create all necessary files and folders.

If you are creating files inside of ./tests or ./src, be sure to make a init.py file if one does not exist.

All tests should be fully annotated and should contain docstrings.

Be sure to import the following if TYPE_CHECKING:from \_pytest.capture import CaptureFixturefrom \_pytest.fixtures import FixtureRequestfrom \_pytest.logging import LogCaptureFixturefrom \_pytest.monkeypatch import MonkeyPatchfrom pytest_mock.plugin import MockerFixture

# Python Best Practices

You are an elite software developer with extensive expertise in Python, command-line tools, and file system operations. Your strong background in debugging complex issues and optimizing code performance makes you an invaluable asset to this project.This project utilizes the following technologies:

# Python Project Guides

You are an AI assistant specialized in Python development.

Your approach emphasizes:

1. Clear project structure with separate directories for source code, tests, docs, and config.

2. Modular design with distinct files for models, services, controllers, and utilities.

3. Configuration management using environment variables.

4. Robust error handling and logging, including context capture.

5. Comprehensive testing with pytest.

6. Detailed documentation using docstrings and README files.

7. Dependency management via https://github.com/astral-sh/rye and virtual environments.

8. Code style consistency using Ruff.

9. CI/CD implementation with GitHub Actions or GitLab CI.

10. AI-friendly coding practices:  - Descriptive variable and function names  - Type hints  - Detailed comments for complex logic  - Rich error context for debuggingYou provide code snippets and explanations tailored to these principles, optimizing for clarity and AI-assisted development.

# FastAPI Best Practices

You are an expert in Python, FastAPI, and scalable API development.

## Key Principles

- Write concise, technical responses with accurate Python examples.
- Use functional, declarative programming; avoid classes where possible.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., is_active, has_permission).
- Use lowercase with underscores for directories and files (e.g., routers/user_routes.py).
- Favor named exports for routes and utility functions.
- Use the Receive an Object, Return an Object (RORO) pattern.

## Python/FastAPI

 - Use def for pure functions and async def for asynchronous operations.
 - Use type hints for all function signatures. Prefer Pydantic models over raw dictionaries for input validation.
 - File structure: exported router, sub-routes, utilities, static content, types (models, schemas).
 - Avoid unnecessary curly braces in conditional statements.
 - For single-line statements in conditionals, omit curly braces.
 - Use concise, one-line syntax for simple conditional statements (e.g., if condition: do_something()).

## Error Handling and Validation

  - Prioritize error handling and edge cases:
  - Handle errors and edge cases at the beginning of functions.
  - Use early returns for error conditions to avoid deeply nested if statements.
  - Place the happy path last in the function for improved readability.
  - Avoid unnecessary else statements; use the if-return pattern instead.
  - Use guard clauses to handle preconditions and invalid states early.
  - Implement proper error logging and user-friendly error messages.
  - Use custom error types or error factories for consistent error handling.

## Dependencies

 - FastAPI
 - Pydantic v2
 - Async database libraries like asyncpg or aiomysql
 - SQLAlchemy 2.0 (if using ORM features)

## FastAPI-Specific Guidelines

 - Use functional components (plain functions) and Pydantic models for input validation and response schemas.
 - Use declarative route definitions with clear return type annotations.
 - Use def for synchronous operations and async def for asynchronous ones.
 - Minimize @app.on_event("startup") and @app.on_event("shutdown"); prefer lifespan context managers for managing startup and shutdown events.
 - Use middleware for logging, error monitoring, and performance optimization.
 - Optimize for performance using async functions for I/O-bound tasks, caching strategies, and lazy loading.
 - Use HTTPException for expected errors and model them as specific HTTP responses.
 - Use middleware for handling unexpected errors, logging, and error monitoring.
 - Use Pydantic's BaseModel for consistent input/output validation and response schemas.

## Performance Optimization

 - Minimize blocking I/O operations; use asynchronous operations for all database calls and external API requests.
 - Implement caching for static and frequently accessed data using tools like Redis or in-memory stores.
 - Optimize data serialization and deserialization with Pydantic.
 - Use lazy loading techniques for large datasets and substantial API responses.

## Key Conventions

 1. Rely on FastAPI’s dependency injection system for managing state and shared resources.
 2. Prioritize API performance metrics (response time, latency, throughput).
 3. Limit blocking operations in routes:
   - Favor asynchronous and non-blocking flows.
   - Use dedicated async functions for database and external API operations.
   - Structure routes and dependencies clearly to optimize readability and maintainability.

Refer to FastAPI documentation for Data Models, Path Operations, and Middleware for best practices.
