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
