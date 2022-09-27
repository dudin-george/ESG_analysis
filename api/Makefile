# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
isort = isort app/
black = black app/
mypy = mypy app/
flake8  = flake8 app/

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
	$(flake8)
	# $(mypy)

.PHONY: all
all: format
