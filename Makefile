.PHONY: help dev-front dev-back prod build-frontend down clean logs shell migrate

#==============================================================================
# DEFAULT TARGET
#==============================================================================

help:
	@echo "========================================================="
	@echo "|  Available Commands"
	@echo "========================================================="
	@echo "|"
	@echo "|    make                  - Show this help message"
	@echo "|    make help             - Show this help message"
	@echo "|"
	@echo "|= Development:"
	@echo "|    make dev-front        - Frontend development. Vite runs separately and uses"
	@echo "|                            environment variables in .env.dev_front"
	@echo "|    make dev-front-bg     - Same as dev-front but running in the background"
	@echo "|    make dev-back         - Backend development. Frontend is served statically in"
	@echo "|                            the same process. Uses .env.dev_back variables"
	@echo "|                            NOTE: Assumes the frontend is ready to build"
	@echo "|    make dev-back-bg      - Same as dev-back but running in the background"
	@echo "|"
	@echo "|= Production:"
	@echo "|    make prod             - Production mode using .env.prod variables"
	@echo "|    make prod-bg          - Same as prod but in the background"
	@echo "|"
	@echo "|= Building:"
	@echo "|    make build-frontend   - Build frontend only"
	@echo "|    make build-all        - Build all images"
	@echo "|    make force-rebuild    - Rebuild images without the cache"
	@echo "|"
	@echo "|= Logs:"
	@echo "|    make logs             - View all logs"
	@echo "|    make logs-frontend    - View frontend logs only"
	@echo "|    make logs-backend     - View backend logs only"
	@echo "|    make logs-postgres    - View postgres logs only"
	@echo "|"
	@echo "|= Database:"
	@echo "|    make backup-db        - Create a database backup in ./backups/CURRENT_PROFILE"
	@echo "|    make restore-db       - Restores a database backup from ./backups/CURRENT_PROFILE"
	@echo "|"
	@echo "|= Operating:"
	@echo "|    make ps               - Show container status"
	@echo "|    make down             - Stop all containers"
	@echo "|    make restart-frontend - Restart the frontend container"
	@echo "|    make restart-backend  - Restart the backend container"
	@echo "|    make shell-backend    - Open bash in backend container"
	@echo "|    make shell-postgres   - Open psql in postgres container"
	@echo "|    make clean            - Stop & remove volumes (WARNING: deletes DB)"
	@echo "|"
	@echo "|"
	@echo "| NOTE: Make sure the containers are up and running before"
	@echo "|       you run the Logs, Database,  or Operating commands"
	@echo "|       Otherwise, the process will exit with error code 1"
	@echo "|"
	@echo "========================================================="

#==============================================================================
# DEVELOPMENT TARGETS
#==============================================================================

# Frontend development (Vite server)
dev-front:
	@echo "Starting FRONTEND development mode..."
	docker-compose --env-file .env.dev_front --profile dev_front up

dev-front-bg:
	@echo "Starting FRONTEND development mode in the background..."
	docker-compose --env-file .env.dev_front --profile dev_front up -d

# Backend development (serves pre-built frontend statically)
dev-back: check-frontend-built
	@echo "Starting BACKEND development mode..."
	docker-compose --env-file .env.dev_back --profile dev_back up

dev-back-bg: check-frontend-built
	@echo "Starting BACKEND development mode in the background..."
	docker-compose --env-file .env.dev_back --profile dev_back up -d

#==============================================================================
# PRODUCTION TARGETS
#==============================================================================

prod:
	@echo "Starting PRODUCTION mode..."
	docker-compose --env-file .env.prod --profile prod up

prod-bg:
	@echo "Starting PRODUCTION mode in the background..."
	docker-compose --env-file .env.prod --profile prod up -d

#==============================================================================
# BUILD TARGETS
#==============================================================================

build-frontend:
	@echo "Building frontend..."
	cd frontend && npm install && npm run build

build-all:
	@echo "Building all Docker images..."
	docker-compose build

force-rebuild:
	@echo "Rebuilding images without the cache..."
	docker-compose build --no-cache

check-frontend-built:
	@if [ ! -d "frontend/dist" ]; then \
		echo "Frontend not built yet, building now..."; \
		$(MAKE) build-frontend; \
	fi

#==============================================================================
# LOG TARGETS
#==============================================================================

logs:
	@echo "Showing all logs..."
	docker-compose logs -f

logs-backend:
	@echo "Showing backend logs..."
	docker-compose logs -f backend

logs-frontend:
	@echo "Showing frontend logs..."
	docker-compose logs -f frontend

logs-postgres:
	@echo "Showing postgres logs..."
	docker-compose logs -f postgres

#==============================================================================
# DATABASE TARGETS
#==============================================================================

backup-db:
	@echo "Creating database backup..."
	@if docker-compose ps | grep -q "dev_front.*Up"; then \
		mkdir -p backups/front; \
		set -a && . .env.dev_front && set +a && \
		user=$$POSTGRES_USER && \
		db=$$POSTGRES_DB && \
		file="backups/front/front_backup_$$(date +%Y%m%d_%H%M%S).sql" && \
		docker-compose exec -T postgres pg_dump -U $$user $$db > $$file && \
		echo "[SUCCESS] Backup created: $$file"; \
	elif docker-compose ps | grep -q "dev_back.*Up"; then \
		mkdir -p backups/back; \
		set -a && . .env.dev_back && set +a && \
		user=$$POSTGRES_USER && \
		db=$$POSTGRES_DB && \
		file="backups/back/back_backup_$$(date +%Y%m%d_%H%M%S).sql" && \
		docker-compose exec -T postgres pg_dump -U $$user $$db > $$file && \
		echo "[SUCCESS] Backup created: $$file"; \
	elif docker-compose ps | grep -q "prod.*Up"; then \
		mkdir -p backups/prod; \
		set -a && . .env.prod && set +a && \
		user=$$POSTGRES_USER && \
		db=$$POSTGRES_DB && \
		file="backups/prod/prod_backup_$$(date +%Y%m%d_%H%M%S).sql" && \
		docker-compose exec -T postgres pg_dump -U $$user $$db > $$file && \
		echo "[SUCCESS] Backup created: $$file"; \
	else \
		echo "[ERROR] No containers running. Start containers first with 'make dev-front', 'make dev-back', or 'make prod'"; \
		exit 1; \
	fi

restore-db:
	@echo "Detecting running profile..."
	@if docker-compose ps | grep -q "dev_front.*Up"; then \
		echo "Available backups in backups/front:"; \
		ls -1 backups/front/*.sql 2>/dev/null || (echo "No backups found" && exit 1); \
		echo ""; \
		read -p "Enter backup filename: " backup; \
		if [ -f "$$backup" ]; then \
			read -p "WARNING: This will OVERWRITE the current database. Continue? [y/N] " confirm; \
			if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
				set -a && . .env.dev_front && set +a && \
				docker-compose exec -T postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB < $$backup && \
				echo "[SUCCESS] Database restored from $$backup"; \
			else \
				echo "[CANCELLED]"; \
			fi; \
		else \
			echo "[ERROR] Backup file not found: $$backup"; \
		fi; \
	elif docker-compose ps | grep -q "dev_back.*Up"; then \
		echo "Available backups in backups/back:"; \
		ls -1 backups/back/*.sql 2>/dev/null || (echo "No backups found" && exit 1); \
		echo ""; \
		read -p "Enter backup filename: " backup; \
		if [ -f "$$backup" ]; then \
			read -p "WARNING: This will OVERWRITE the current database. Continue? [y/N] " confirm; \
			if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
				set -a && . .env.dev_back && set +a && \
				docker-compose exec -T postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB < $$backup && \
				echo "[SUCCESS] Database restored from $$backup"; \
			else \
				echo "[CANCELLED]"; \
			fi; \
		else \
			echo "[ERROR] Backup file not found: $$backup"; \
		fi; \
	elif docker-compose ps | grep -q "prod.*Up"; then \
		echo "Available backups in backups/prod:"; \
		ls -1 backups/prod/*.sql 2>/dev/null || (echo "No backups found" && exit 1); \
		echo ""; \
		read -p "Enter backup filename: " backup; \
		if [ -f "$$backup" ]; then \
			read -p "WARNING: This will OVERWRITE the current database. Continue? [y/N] " confirm; \
			if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
				set -a && . .env.prod && set +a && \
				docker-compose exec -T postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB < $$backup && \
				echo "[SUCCESS] Database restored from $$backup"; \
			else \
				echo "[CANCELLED]"; \
			fi; \
		else \
			echo "[ERROR] Backup file not found: $$backup"; \
		fi; \
	else \
		echo "[ERROR] No containers running. Start containers first with 'make dev-front', 'make dev-back', or 'make prod'"; \
		exit 1; \
	fi

#==============================================================================
# OPERATING TARGETS
#==============================================================================

ps:
	@echo "========================================================"
	@echo "  Container Status"
	@echo "========================================================"
	@echo ""
	@docker-compose ps
	@echo ""
	@echo "========================================================"

down:
	@echo "Stopping all containers..."
	@if docker-compose ps -q | grep -q .; then \
		docker-compose --profile "*" down; \
	else \
		echo "[ERROR] No containers running."; \
		exit 1; \
	fi

restart-frontend:
	@echo "Restarting frontend..."
	docker-compose restart frontend

restart-backend:
	@echo "Restarting backend..."
	docker-compose restart backend

shell-backend:
	@echo "Opening shell in backend container..."
	docker-compose exec backend bash

shell-postgres:
	@if docker-compose ps | grep -q "dev_front.*Up"; then \
		echo "Opening psql in postgres container using dev_front environment..."; \
		set -a && . .env.dev_front && set +a && \
		docker-compose exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB; \
	elif docker-compose ps | grep -q "dev_back.*Up"; then \
		echo "Opening psql in postgres container using dev_back environment..."; \
		set -a && . .env.dev_back && set +a && \
		docker-compose exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB; \
	elif docker-compose ps | grep -q "prod.*Up"; then \
		echo "Opening psql in postgres container using prod environment..."; \
		set -a && . .env.prod && set +a && \
		docker-compose exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB; \
	else \
		echo "No containers running. Start the containers first"; \
		exit 1; \
	fi

clean:
	@echo "Cleaning everything (including database)..."
	@if docker-compose ps -q | grep -q .; then \
		read -p "WARNING: Are you sure? This will DELETE ALL DATA! [y/N] " confirm; \
		if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
			docker-compose --profile "*" down -v; \
			echo "[SUCCESS] Cleaned!"; \
		else \
			echo "[CANCELLED]"; \
			echo ""; \
			echo "Containers are still running."; \
			echo "If you want to stop the containers, run: make down"; \
		fi \
	else \
		echo "[ERROR] No containers running."; \
		exit 1; \
	fi