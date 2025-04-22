.PHONY: build up down restart logs shell static migrate makemigrations test superuser ruff check format clean run docs

# Docker Compose commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

# Django commands
static:
	docker-compose exec web python manage.py collectstatic --no-input

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

test:
	docker-compose exec web pytest

superuser:
	docker-compose exec web python manage.py createsuperuser

# Development
run:
	python manage.py runserver 0.0.0.0:8000

docs:
	echo "API Documentation is available at:"
	echo "  - Swagger UI: http://localhost:8000/swagger/"
	echo "  - ReDoc: http://localhost:8000/redoc/"

# Code quality
ruff:
	ruff check .

check:
	python manage.py check --deploy

format:
	ruff format .

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Help
help:
	@echo "Available commands:"
	@echo "build          - Build the Docker containers"
	@echo "up             - Start the Docker containers"
	@echo "down           - Stop the Docker containers"
	@echo "restart        - Restart the Docker containers"
	@echo "logs           - Show logs from containers"
	@echo "shell          - Open Django shell"
	@echo "static         - Collect static files"
	@echo "migrate        - Run migrations"
	@echo "makemigrations - Create new migrations"
	@echo "test           - Run tests"
	@echo "superuser      - Create superuser"
	@echo "run            - Run development server"
	@echo "docs           - Show API documentation URLs"
	@echo "ruff           - Run code linting"
	@echo "check          - Run Django deployment checks"
	@echo "format         - Format code with ruff"
	@echo "clean          - Remove cache files" 