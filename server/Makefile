# Dependency Install
install:
	@echo "Installing dependencies..."
	uv sync

dev: 
	@echo "Starting development server..."
	@if [ -f .env ]; then \
		echo ".env file found"; \
		set -a && . ./.env && set +a && ENV=development uv run python main.py; \
	else \
		echo ".env file not found"; \
		ENV=development uv run python main.py; \
	fi

local:
	@echo "Starting server in local environment (.env.local file used)"
	@if [ -f .env.local ]; then \
		echo ".env.local file found"; \
		set -a && . ./.env.local && set +a && ENV=local uv run python main.py; \
	else \
		echo ".env.local file not found"; \
		echo "Create a .env.local file or use the 'make dev' command"; \
		exit 1; \
	fi

# Run tests
test:
	@echo "Running tests..."
	uv run pytest tests/ -v

# --- LangGraph (see docs/agent-purpose.md) ---
.PHONY: langgraph-dev agent-smoke

langgraph-dev:
	@echo "Starting LangGraph dev server (http://127.0.0.1:2024)..."
	@if [ -f .env ]; then \
		set -a && . ./.env && set +a; \
	fi
	uv run langgraph dev

agent-smoke:
	@echo "Running meeting_summary graph (mock mode)..."
	@if [ -f .env ]; then \
		set -a && . ./.env && set +a; \
	fi
	uv run python scripts/smoke_meeting_summary.py

# --- Database migrations (Alembic) ---
# Examples:
#   make db-upgrade
#   make db-downgrade
#   make db-downgrade-base
#   make db-revision MSG=add_posts_table
#   make db-history

.PHONY: db-upgrade db-downgrade db-downgrade-base db-revision db-history db-current db-heads

db-upgrade:
	@echo "Applying migrations (upgrade head)..."
	uv run alembic upgrade head

db-downgrade:
	@echo "Reverting one migration (downgrade -1)..."
	uv run alembic downgrade -1

db-downgrade-base:
	@echo "Reverting all migrations (downgrade base)..."
	uv run alembic downgrade base

db-revision:
	@if [ -z "$(MSG)" ]; then \
		echo "MSG is required. Example: make db-revision MSG=add_posts_table"; \
		exit 1; \
	fi
	@echo "Generating autogenerate revision: $(MSG)"
	uv run alembic revision --autogenerate -m "$(MSG)"

db-history:
	uv run alembic history

db-current:
	uv run alembic current

db-heads:
	uv run alembic heads
