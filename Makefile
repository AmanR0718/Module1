.PHONY: help build up down logs clean test init-db

help:
	@echo "Zambian Farmer Support System - Available Commands:"
	@echo "  make build      - Build Docker containers"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs"
	@echo "  make clean      - Remove all containers and volumes"
	@echo "  make test       - Run tests"
	@echo "  make init-db    - Initialize database with sample data"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "MongoDB: localhost:27017"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf uploads/

test:
	cd backend && python -m pytest tests/

init-db:
	docker-compose exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin zambian_farmers /docker-entrypoint-initdb.d/init.js

restart:
	docker-compose restart

ps:
	docker-compose ps