PROJECT_PATH := ./lms/
TEST_PATH := ./tests/


HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

develop: ##@Deps Installing dependencies
	poetry -V
	poetry install

local:
	docker-compose -f docker-compose.dev.yaml up --force-recreate --renew-anon-volumes --build

test: ##@Test Run tests
	pytest $(TEST_PATH) -vx

lint: ##@Code Check project with mypy and ruff
	poetry run mypy $(PROJECT_PATH)
	poetry run ruff check $(PROJECT_PATH) $(TEST_PATH)

format: ##@Code Format project
	poetry run ruff format $(PROJECT_PATH) $(TEST_PATH)