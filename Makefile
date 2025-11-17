.PHONY:help 

help:       
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

up: ## Start all services defined in compose.yml without rebuilding
	@echo "Starting all services defined in compose.yml..."
	docker compose up 
	
down: ## Stop and remove all containers
	@echo "Stopping and removing all containers..."
	docker compose down

clean: ## Stop and remove all containers and volumes
	@echo "Stopping and removing all containers and volumes..."
	docker compose down --volumes
	
migrations: ## Create new database migrations
	poetry run python django-app/manage.py makemigrations

migrate: ## Apply database migrations
	poetry run python django-app/manage.py migrate

## ----------------------------------------------------------------------------
## Setup commands before starting the services
## ----------------------------------------------------------------------------

compose.setup: ## 1 - Setup Docker Compose environment (migrations + migrate)
	@$(MAKE) compose.migrate

up-build: compose.createsuperuser ## 2 - Start all services defined in compose.yml with rebuilding and creating superuser
	@echo "Starting all services defined in compose.yml with rebuilding..."
	docker compose up --build

## ----------------------------------------------------------------------------
## Commands to run inside the running Docker container
## ----------------------------------------------------------------------------

compose.migrations: ## Create new database migrations on service running...
	docker compose run --rm app poetry run python django-app/manage.py makemigrations

compose.migrate: compose.migrations ## Apply database migrations on service running...
	@echo "🛠️  Applying migrations inside Docker container..."
	docker compose run --rm app poetry run python django-app/manage.py migrate

compose.createsuperuser:  ## Create a superuser on service running...
	@echo "👤 Creating superuser inside Docker container..."
	docker compose run --rm app poetry run python django-app/manage.py createsuperuser

createadmin:
	docker compose run --rm app poetry run python django-app/manage.py shell -c "from library.models import Users; \
	Users.objects.create(name='admin', email='admin@example.com', password='Admin123', role='admin'); \
	print('Admin user created successfully.')"

compose.createusers: ## Create admin user on service running...
	docker compose run --rm app poetry run python django-app/create_userAdmin.py

compose.load-books: ## Load books into the running Docker Django container
	@echo "📚 Loading books inside Docker container..."
	docker compose run --rm app poetry run python django-app/manage.py load_books_data ./books.json
## ----------------------------------------------------------------------------

prune: ## Delete all containers
	docker system prune -a