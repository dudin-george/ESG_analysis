# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
isort = isort .
black = black .
mypy = mypy .
flake8  = flake8 .

.PHONY: install-linting
install-linting:
	poetry add flake8 black isort mypy -D
	pre-commit install

.PHONY: install
install: install-linting
	@echo 'installed development requirements'

.PHONY: lint
lint:
	$(isort) --df --check-only
	$(black) --diff --check
	$(flake8)

.PHONY: format
format:
	$(isort)
	$(black)
	$(mypy)
	$(flake8)

.PHONY: up
up:
	docker compose up -d --build --remove-orphans

.PHONY: up-api
up-api:
	docker compose up -d --build api database --remove-orphans

.PHONY: all
all: format
