.PHONY: help dev-front dev-front-bg dev-back dev-back-bg production production-bg \
        build-frontend build-frontend-nc build-backend build-backend-nc \
        all-logs frontend-logs backend-logs postgres-logs minio-logs \
        ps down restart-all restart-frontend restart-backend restart-postgres restart-minio \
        shell-backend shell-postgres clean

# Default target
.DEFAULT_GOAL := help

#==============================================================================
# VARIABLES
#==============================================================================

COMPOSE := docker-compose
ENV_DEV_FRONT := .env.front_dev
ENV_DEV_BACK := .env.back_dev
ENV_PRODUCTION := .env.production

#==============================================================================
# HELP
#==============================================================================

help:
	@echo "=========================================================="
	@echo "                    Available Commands"
	@echo "=========================================================="
	@echo ""
	@echo "  make  |  make help     - Show this help message"
	@echo ""
	@echo "Development:"
	@echo "  make front-dev         - Frontend dev mode (Vite hot reload)"
	@echo "  make front-dev-bg      - Frontend dev mode (background)"
	@echo "  make back-dev          - Backend dev mode (FastAPI hot reload)"
	@echo "  make back-dev-bg       - Backend dev mode (background)"
	@echo ""
	@echo "Production:"
	@echo "  make production        - Production mode (static frontend)"
	@echo "  make production-bg     - Production mode (background)"
	@echo ""
	@echo "Building:"
	@echo "  make build-frontend    - Build frontend with cache"
	@echo "  make build-frontend-nc - Build frontend without cache"
	@echo "  make build-backend     - Build backend with cache"
	@echo "  make build-backend-nc  - Build backend without cache"
	@echo ""
	@echo "Logs:"
	@echo "  make all-logs          - View all logs"
	@echo "  make frontend-logs     - View frontend logs"
	@echo "  make backend-logs      - View backend logs"
	@echo "  make postgres-logs     - View postgres logs"
	@echo "  make minio-logs        - View minio logs"
	@echo ""
	@echo "Operations:"
	@echo "  make ps                - Show container status"
	@echo "  make down              - Stop all containers"
	@echo "  make restart-all       - Restart all containers"
	@echo "  make restart-frontend  - Restart frontend container"
	@echo "  make restart-backend   - Restart backend container"
	@echo "  make restart-postgres  - Restart postgres container"
	@echo "  make restart-minio     - Restart minio container"
	@echo "  make shell-backend     - Open bash in backend container"
	@echo "  make shell-postgres    - Open psql in postgres container"
	@echo "  make clean             - Stop & remove volumes (deletes data!)"
	@echo ""
	@echo "=========================================================="

#==============================================================================
# DEVELOPMENT TARGETS
#==============================================================================

front-dev:
	@echo "Starting frontend development mode..."
	@ln -sf $(ENV_DEV_FRONT) .env && test -L .env
	@$(COMPOSE) --profile front-dev up

front-dev-bg:
	@echo "Starting frontend development mode (background)..."
	@ln -sf $(ENV_DEV_FRONT) .env && test -L .env
	@$(COMPOSE) --profile front-dev up -d
	@echo "Containers started. Use 'make all-logs' to view logs"

back-dev:
	@echo "Starting backend development mode..."
	@ln -sf $(ENV_DEV_BACK) .env
	@$(MAKE) build-frontend
	@$(COMPOSE) --profile back-dev up

back-dev-bg:
	@echo "Starting backend development mode (background)..."
	@ln -sf $(ENV_DEV_BACK) .env && test -L .env
	@$(MAKE) build-frontend
	@$(COMPOSE) --profile back-dev up -d
	@echo "Containers started. Use 'make all-logs' to view logs"

#==============================================================================
# PRODUCTION TARGETS
#==============================================================================

production: build-frontend
	@echo "Starting production mode..."
	@ln -sf $(ENV_PRODUCTION) .env && \
		$(COMPOSE) --profile prod up

production-bg: build-frontend
	@echo "Starting production mode (background)..."
	@ln -sf $(ENV_PRODUCTION) .env && \
		$(COMPOSE) --profile prod up -d
	@echo "Containers started. Use 'make all-logs' to view logs"

#==============================================================================
# BUILD TARGETS
#==============================================================================

build-frontend:
	@echo "Building frontend..."
	@$(COMPOSE) build frontend

build-frontend-nc:
	@echo "Building frontend without cache..."
	@$(COMPOSE) build --no-cache frontend

build-backend:
	@echo "Building backend..."
	@$(COMPOSE) build backend

build-backend-nc:
	@echo "Building backend without cache..."
	@$(COMPOSE) build --no-cache backend

#==============================================================================
# LOG TARGETS
#==============================================================================

all-logs:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "Showing all logs..."; \
		$(COMPOSE) logs -f; \
	else \
		echo "ERROR: No containers running"; \
		exit 1; \
	fi

frontend-logs:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "Showing frontend logs..."; \
		$(COMPOSE) logs -f frontend; \
	else \
		echo "ERROR: No containers running"; \
		exit 1; \
	fi

backend-logs:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "Showing backend logs..."; \
		$(COMPOSE) logs -f backend; \
	else \
		echo "ERROR: No containers running"; \
		exit 1; \
	fi

postgres-logs:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "Showing postgres logs..."; \
		$(COMPOSE) logs -f postgres; \
	else \
		echo "ERROR: No containers running"; \
		exit 1; \
	fi

minio-logs:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "Showing minio logs..."; \
		$(COMPOSE) logs -f minio; \
	else \
		echo "ERROR: No containers running"; \
		exit 1; \
	fi

#==============================================================================
# OPERATING TARGETS
#==============================================================================

ps:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "================================================================="; \
		echo "                     Container Status"; \
		echo "================================================================="; \
		echo ""; \
		$(COMPOSE) ps; \
		echo ""; \
		echo "================================================================="; \
	else \
		echo "ERROR: No containers running"; \
		exit 1; \
	fi

down:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "Stopping all containers..."; \
		$(COMPOSE) --profile "*" down; \
		rm .env; \
	else \
		echo "ERROR: No containers running"; \
		rm .env > /dev/null; \
		exit 1; \
	fi

restart-all:
	@echo "Restarting all containers..."
	@$(COMPOSE) --profile "*" restart

restart-frontend:
	@echo "Restarting frontend..."
	@$(COMPOSE) restart frontend

restart-backend:
	@echo "Restarting backend..."
	@$(COMPOSE) restart backend

restart-postgres:
	@echo "Restarting postgres..."
	@$(COMPOSE) restart postgres

restart-minio:
	@echo "Restarting minio..."
	@$(COMPOSE) restart minio

shell-backend:
	@echo "Opening shell in backend container..."
	@$(COMPOSE) exec backend bash

shell-postgres:
	@echo "Opening psql in postgres container..."
	@set -a && . .env && set +a && \
		$(COMPOSE) exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB

clean:
	@echo "WARNING: This will DELETE ALL DATA including the database!"
	@echo -n "Are you sure you want to continue? [y/N] " && read confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "Cleaning everything..."; \
		$(COMPOSE) --profile "*" down -v; \
		rm .env; \
		echo "SUCCESS: Cleaned!"; \
	else \
		echo "CANCELLED: No changes made"; \
	fi

nuke:
	@echo "🔥 Nuking everything..."
	@docker-compose down -v 2>/dev/null || true
	@docker stop $$(docker ps -aq) 2>/dev/null || true
	@docker rm $$(docker ps -aq) 2>/dev/null || true
	@docker rmi $$(docker images -q) --force 2>/dev/null || true
	@docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	@docker network prune -f 2>/dev/null || true
	@docker builder prune -a -f 2>/dev/null || true
	@docker buildx prune -a -f 2>/dev/null || true
	@docker system prune -a --volumes -f 2>/dev/null || true
	@echo "✅ Everything nuked!"