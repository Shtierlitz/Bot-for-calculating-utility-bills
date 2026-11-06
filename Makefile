# Variables can be overridden via `make VAR=value target`
PROJECT_NAME ?= utility-bot
IMAGE_NAME ?= $(PROJECT_NAME):latest
CONTAINER_NAME ?= $(PROJECT_NAME)
ENV_FILE ?= .env
DOCKER_RUN_FLAGS ?= --rm

# Local development (Python version matches the Docker image)
PYTHON ?= python3.12
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
PYTEST_FLAGS ?= -vv -ra --tb=long --showlocals --log-cli-level=INFO
PYTEST_ARGS ?=

.PHONY: help venv test lint pre-commit pre-commit-install build run up stop restart logs shell clean

help:
	@echo "Useful targets:"
	@echo "  make venv           - create $(VENV) with $(PYTHON) and install requirements-dev.txt"
	@echo "  make test           - run pytest from $(VENV) (extra args: PYTEST_ARGS=\"tests/test_config.py -k name\")"
	@echo "  make lint           - run Ruff checks for bot and tests"
	@echo "  make pre-commit     - run all pre-commit hooks for the repository"
	@echo "  make pre-commit-install - install the pre-commit git hook"
	@echo "  make build          - build Docker image ($(IMAGE_NAME))"
	@echo "  make run            - run container in foreground"
	@echo "  make up             - run container detached (always-on)"
	@echo "  make stop           - stop running container"
	@echo "  make restart        - restart running container"
	@echo "  make logs           - follow container logs"
	@echo "  make shell          - open bash inside running container"
	@echo "  make clean          - remove container and image"

venv:
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "$(PYTHON) not found. Install Python 3.12 or run: make venv PYTHON=/path/to/python3.12"; exit 1; }
	@test -x $(VENV_PYTHON) || $(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt

test:
	@test -x $(VENV_PYTHON) || { echo "$(VENV) not found. Run: make venv"; exit 1; }
	$(VENV_PYTHON) -m pytest $(PYTEST_FLAGS) $(PYTEST_ARGS)

lint:
	@test -x $(VENV_PYTHON) || { echo "$(VENV) not found. Run: make venv"; exit 1; }
	$(VENV_PYTHON) -m ruff check bot tests

pre-commit:
	@test -x $(VENV_PYTHON) || { echo "$(VENV) not found. Run: make venv"; exit 1; }
	$(VENV_PYTHON) -m pre_commit run --all-files

pre-commit-install:
	@test -x $(VENV_PYTHON) || { echo "$(VENV) not found. Run: make venv"; exit 1; }
	$(VENV_PYTHON) -m pre_commit install

build:
	docker build -t $(IMAGE_NAME) .

run: build
	docker run $(DOCKER_RUN_FLAGS) --env-file $(ENV_FILE) --name $(CONTAINER_NAME) $(IMAGE_NAME)

up: build
	docker run -d $(DOCKER_RUN_FLAGS) --env-file $(ENV_FILE) --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME) || true

restart:
	docker restart $(CONTAINER_NAME)

logs:
	docker logs -f $(CONTAINER_NAME)

shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

clean:
	-docker rm -f $(CONTAINER_NAME)
	-docker rmi $(IMAGE_NAME)
