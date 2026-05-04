# syntax=docker/dockerfile:1
# Build context: repository root (monorepo).

FROM node:22-bookworm-slim AS builder

WORKDIR /app

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY apps/web/package.json apps/web/
COPY packages/ui/package.json packages/ui/
COPY packages/core/package.json packages/core/

RUN pnpm install --frozen-lockfile

COPY apps/web apps/web
COPY packages/ui packages/ui
COPY packages/core packages/core

RUN pnpm --filter @conflow/web build

FROM nginx:1.27-alpine AS runner

COPY docker/nginx-web.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
