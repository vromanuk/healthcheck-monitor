.EXPORT_ALL_VARIABLES:
COMPOSE_FILE ?= docker-compose-local.yml
COMPOSE_PROJECT_NAME ?= statsd
DOTENV_BASE_FILE ?= .env-local
-include $(DOTENV_BASE_FILE)

fmt:
	pipenv run black .
	pipenv run isort .

test:
	pipenv run pytest

lint:
	pipenv run black . --check
	pipenv run isort . --check
	pipenv run mypy ./statsd

install:
	pip install pipenv
	pipenv install

docker-up:
	docker-compose up --remove-orphans -d
	docker-compose ps

docker-down:
	docker-compose down

consumer:
	python3 -m statsd.stats_collector.main

producer:
	python3 -m statsd.statsd_exporter.main