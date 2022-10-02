# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
isort = isort app/ tests/
black = black app/ tests/
mypy = mypy app/
flake8  = flake8 app/ tests/

.PHONY: install-linting
install-linting:
	poetry add flake8 black isort mypy -G dev
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

.PHONY: export-dependencies
export-dependencies:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

.PHONY: database
database:
	docker run --name postgresql -e POSTGRES_USER=myusername -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -d postgres

.PHONY: test
test:
	docker compose -f docker-compose.test.yaml up --build

.PHONY: all
all: format export-dependencies
