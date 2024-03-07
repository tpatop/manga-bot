DC = docker-compose
DEV_COMPOSE = -f dev.docker-compose.yml

.PHONY: start-dev start-dev-rebuild migrate stop delete

start-dev: ## up development version (add -d for detaching mode)
	$(DC) $(DEV_COMPOSE) up

start-dev-rebuild: ## development version with container rebuild
	$(DC) $(DEV_COMPOSE) up --build

migrate: ## alembic migration
	docker exec bot alembic upgrade head

stop: ## stop all containers
	docker stop $$(docker ps -a -q) || true

delete: ## delete all containers/images
	docker system prune -a --volumes