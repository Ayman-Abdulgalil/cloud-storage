.PHONY: help front-dev front-dev-bg back-dev back-dev-bg production production-bg \
        build-vite build-vite-nc build-fastapi build-fastapi-nc \
        all-logs vite-logs fastapi-logs postgres-logs minio-logs \
        ps down restart-all restart-vite restart-fastapi restart-postgres restart-minio \
        shell-fastapi shell-postgres clean

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
	@echo "  make build-vite        - Build vite with cache"
	@echo "  make build-vite-nc     - Build vite without cache"
	@echo "  make build-fastapi     - Build fastapi with cache"
	@echo "  make build-fastapi-nc  - Build fastapi without cache"
	@echo ""
	@echo "Logs:"
	@echo "  make all-logs          - View all logs"
	@echo "  make vite-logs         - View vite logs"
	@echo "  make fastapi-logs      - View fastapi logs"
	@echo "  make postgres-logs     - View postgres logs"
	@echo "  make minio-logs        - View minio logs"
	@echo ""
	@echo "Operations:"
	@echo "  make ps                - Show container status"
	@echo "  make down              - Stop all containers"
	@echo "  make restart-all       - Restart all containers"
	@echo "  make restart-vite      - Restart vite container"
	@echo "  make restart-fastapi   - Restart fastapi container"
	@echo "  make restart-postgres  - Restart postgres container"
	@echo "  make restart-minio     - Restart minio container"
	@echo "  make shell-fastapi     - Open bash in fastapi container"
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

back-dev: check-frontend-built
	@echo "Starting backend development mode..."
	@ln -sf $(ENV_DEV_BACK) .env
	@$(COMPOSE) --profile back-dev up

back-dev-bg: check-frontend-built
	@echo "Starting backend development mode (background)..."
	@ln -sf $(ENV_DEV_BACK) .env && test -L .env
	@$(COMPOSE) --profile back-dev up -d
	@echo "Containers started. Use 'make all-logs' to view logs"

#==============================================================================
# PRODUCTION TARGETS
#==============================================================================

production:  check-frontend-built
	@echo "Starting production mode..."
	@ln -sf $(ENV_PRODUCTION) .env && \
		$(COMPOSE) --profile production up

production-bg: check-frontend-built
	@echo "Starting production mode (background)..."
	@ln -sf $(ENV_PRODUCTION) .env && \
		$(COMPOSE) --profile production up -d
	@echo "Containers started. Use 'make all-logs' to view logs"

#==============================================================================
# BUILD TARGETS
#==============================================================================

build-vite:
	@echo "Building vite..."
	@$(COMPOSE) build vite

build-vite-nc:
	@echo "Building vite without cache..."
	@$(COMPOSE) build --no-cache vite

build-fastapi:
	@echo "Building backend..."
	@$(COMPOSE) build fastapi

build-fastapi-nc:
	@echo "Building backend without cache..."
	@$(COMPOSE) build --no-cache fastapi

check-frontend-built:
	@if [ ! -d "frontend/dist" ]; then \
		echo "Frontend not built yet, building now..."; \
		$(MAKE) build-vite; \
	fi

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

vite-logs:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "Showing vite logs..."; \
		$(COMPOSE) logs -f vite; \
	else \
		echo "ERROR: No containers running"; \
		exit 1; \
	fi

fastapi-logs:
	@if $(COMPOSE) ps -q | grep -q .; then \
		echo "Showing fastapi logs..."; \
		$(COMPOSE) logs -f fastapi; \
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

restart-vite:
	@echo "Restarting vite..."
	@$(COMPOSE) restart vite

restart-fastapi:
	@echo "Restarting fastapi..."
	@$(COMPOSE) restart fastapi

restart-postgres:
	@echo "Restarting postgres..."
	@$(COMPOSE) restart postgres

restart-minio:
	@echo "Restarting minio..."
	@$(COMPOSE) restart minio

shell-fastapi:
	@echo "Opening shell in fastapi container..."
	@$(COMPOSE) exec fastapi bash

shell-postgres:
	@echo "Opening psql in postgres container..."
	@set -a && . .env && set +a && \
		$(COMPOSE) exec postgres psql -U $$APP_USER -d $$POSTGRES_DB

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
	@rm .env > /dev/null
	@echo "✅ Everything nuked!"