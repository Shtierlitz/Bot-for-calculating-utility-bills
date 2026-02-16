# Variables can be overridden via `make VAR=value target`
PROJECT_NAME ?= utility-bot
IMAGE_NAME ?= $(PROJECT_NAME):latest
CONTAINER_NAME ?= $(PROJECT_NAME)
ENV_FILE ?= .env
DOCKER_RUN_FLAGS ?= --rm

.PHONY: help build run up stop logs shell clean

help:
	@echo "Useful targets:"
	@echo "  make build          - build Docker image ($(IMAGE_NAME))"
	@echo "  make run            - run container in foreground"
	@echo "  make up             - run container detached (always-on)"
	@echo "  make stop           - stop running container"
	@echo "  make logs           - follow container logs"
	@echo "  make shell          - open bash inside running container"
	@echo "  make clean          - remove container and image"

build:
	docker build -t $(IMAGE_NAME) .

run: build
	docker run $(DOCKER_RUN_FLAGS) --env-file $(ENV_FILE) --name $(CONTAINER_NAME) $(IMAGE_NAME)

up: build
	docker run -d $(DOCKER_RUN_FLAGS) --env-file $(ENV_FILE) --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME) || true

logs:
	docker logs -f $(CONTAINER_NAME)

shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

clean:
	-docker rm -f $(CONTAINER_NAME)
	-docker rmi $(IMAGE_NAME)
