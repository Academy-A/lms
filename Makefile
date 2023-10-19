ifeq($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif


venv: ##@Venv Create new venv


test: ##@Test Run tests
	@POSTGRES_HOST=${POSTGRES_HOST}

