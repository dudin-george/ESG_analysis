# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
isort = isort .
black = black -S -l 120 --target-version py310 .

.PHONY: install-linting
install-linting:
	pip install -r tests/requirements-linting.txt
	pre-commit install

.PHONY: install
install: install-linting
	@echo 'installed development requirements'

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: lint
lint:
	flake8 .
	$(isort) --df   # --check-only
	$(black) --diff # --check

.PHONY: mypy
mypy:
	mypy .

.PHONY: all
all: lint mypy
