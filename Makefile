.PHONY: help install migrate superuser run test clean lint format docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install dependencies"
	@echo "  migrate      Run database migrations"
	@echo "  superuser    Create Django superuser"
	@echo "  run          Run development server"
	@echo "  test         Run test suite"
	@echo "  clean        Clean Python cache files"
	@echo "  lint         Run linting (if tools installed)"
	@echo "  format       Format code (if tools installed)"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run with Docker Compose"

# Installation
install:
	pip install -r requirements.txt

# Database
migrate:
	python manage.py migrate

superuser:
	python manage.py createsuperuser

# Development
run:
	python manage.py runserver

# Testing
test:
	python manage.py test core.tests --verbosity=2

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/

# Code Quality (optional - requires black, flake8, isort)
lint:
	-flake8 core/ mtaalamuX/ --max-line-length=88 --extend-ignore=E203,W503
	-black --check --diff core/ mtaalamuX/
	-isort --check-only --diff core/ mtaalamuX/

format:
	-black core/ mtaalamuX/
	-isort core/ mtaalamuX/

# Docker
docker-build:
	docker build -t mtaalamux .

docker-run:
	docker-compose up --build

# Setup all at once
setup: install migrate superuser
	@echo "Setup complete! Run 'make run' to start the server."