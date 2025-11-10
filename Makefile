.PHONY:help 

help:       
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

up: ## Start all services defined in compose.yml without rebuilding
	@echo "Starting all services defined in compose.yml..."
	docker compose up 
	
up-build : ## Start all services defined in compose.yml with rebuilding
	@echo "Starting all services defined in compose.yml with rebuilding..."
	docker compose up --build

down: ## Stop and remove all containers
	@echo "Stopping and removing all containers..."
	docker compose down

clean: ## Stop and remove all containers and volumes
	@echo "Stopping and removing all containers and volumes..."
	docker compose down --volumes

createsuperuser: ## Create a superuser
	poetry run python django-app/manage.py createsuperuser

migrations: ## Create new database migrations
	poetry run python django-app/manage.py makemigrations

migrate: ## Apply database migrations
	poetry run python django-app/manage.py migrate

prune: ## Delete all containers
	docker system prune -a