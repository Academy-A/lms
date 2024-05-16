PROJECT_PATH := ./lms/
TEST_PATH := ./tests/

PYTHON_VERSION := 3.11

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

develop: ##@Deps Installing dependencies
	python$(PYTHON_VERSION) -m venv .venv
	.venv/bin/pip install -U pip poetry
	.venv/bin/poetry config virtualenvs.create false
	.venv/bin/poetry install
	.venv/bin/pre-commit install

local:
	docker compose -f docker-compose.dev.yaml up --force-recreate --renew-anon-volumes --build

test: ##@Test Run tests
	.venv/bin/pytest $(TEST_PATH) -vx

lint: ##@Code Check project with mypy and ruff
	.venv/bin/poetry run mypy $(PROJECT_PATH)
	.venv/bin/poetry run ruff check $(PROJECT_PATH) $(TEST_PATH)

format: ##@Code Format project
	.venv/bin/poetry run ruff format $(PROJECT_PATH) $(TEST_PATH)