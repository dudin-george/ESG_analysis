# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
isort = isort .
black = black .

.PHONY: install-linting
install-linting:
	poetry add flake8 black isort mypy -D
	pre-commit install

.PHONY: install
install: install-linting
	@echo 'installed development requirements'

.PHONY: lint
lint:
	flake8 .
	$(isort) --df --check-only
	$(black) --diff --check

.PHONY: format
format:
	flake8 .
	$(isort)
	$(black)
	mypy .

.PHONY: all
all: format
