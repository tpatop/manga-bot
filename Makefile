DC = docker-compose
DEV_COMPOSE = -f dev.docker-compose.yml

.PHONY: start start-build stop delete

start: ## up development version -d
	$(DC) $(DEV_COMPOSE) up

start-build: ## up development version with build -d
	$(DC) $(DEV_COMPOSE) up --build

stop: ## stop development vesrion
	$(DC) $(DEV_COMPOSE) down

delete: ## delete all containers/images
	docker system prune -a --volumes
