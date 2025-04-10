SHELL = /bin/bash

# Makefile for highkick dashboard project
export PYTHONPATH=./
# Variables
POETRY = poetry
APP_NAME = rag-admin-panel
DOCKER_COMPOSE_FILE=docker-compose -f docker-compose.yml
DOCKER_EXEC_APP=docker exec -it $(APP_NAME)
DOCKER_MIGRATIONS=$(DOCKER_EXEC_APP) $(POETRY) run alembic

# Commands
run:
	source .env && $(DOCKER_COMPOSE_FILE) up --build -d

run-python:
	$(POETRY) run python app/run.py

stop:
	$(DOCKER_COMPOSE_FILE) stop

logs:
	$(DOCKER_COMPOSE_FILE) logs -f

exec:
	$(DOCKER_EXEC_APP) bash

test:
	$(POETRY) run pytest tests --maxfail=2 --cov-fail-under=5 --cov app -vv

format:
	$(POETRY) run black ./app ./tests
	$(POETRY) run isort ./app ./tests

lint:
	$(POETRY) run black --check ./app
	$(POETRY) run isort --check-only ./app
	$(POETRY) run flake8 ./app
	$(POETRY) run mypy ./app

migrations-new:
	@read -p "Enter migration message: " message; \
	$(DOCKER_MIGRATIONS) revision --autogenerate -m "$$message"

migrations-new-python:
	@read -p "Enter migration message: " message; \
	$(POETRY) run alembic revision --autogenerate -m "$$message"

migrations-up:
	$(DOCKER_MIGRATIONS) upgrade head

migrations-up-python:
	$(POETRY) run alembic upgrade head

migrations-down:
	$(DOCKER_MIGRATIONS) downgrade -1

migrations-down-python:
	$(POETRY) run alembic downgrade -1

help:
	@echo "Available commands:"
	@echo "\trun               		Start the Docker containers"
	@echo "\trun-python        		Start the Python server"
	@echo "\tstop              		Stop the Docker containers"
	@echo "\tlogs              		View the Docker logs"
	@echo "\tlogs         			View the app Docker logs"
	@echo "\texec       			Execute a bash shell in the app container"
	@echo "\ttest              		Run the tests"
	@echo "\tformat            		Format the code using Black and isort"
	@echo "\tlint              		Lint the code using Black, isort, flake8, and mypy"
	@echo "\tmigrations-new    		Create a new Alembic migration"
	@echo "\tmigrations-up     		Upgrade the database to the latest migration"
	@echo "\tmigrations-down   		Downgrade the database to the previous migration"
	@echo "\tmigration-new-python	Create a new Alembic migration"
	@echo "\tmigrations-up-python	Upgrade the database to the latest migration"
	@echo "\tmigrations-down-python	Downgrade the database to the previous migration"