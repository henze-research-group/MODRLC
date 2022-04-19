
build:
	docker-compose build

build-nocache:
	docker-compose build --no-cache

remove-image:
	docker-compose rm -sf

run :
	$(MAKE) run-detached
	$(MAKE) provision
	docker-compose logs -f web worker

bash:
	$(COMMAND_RUN) --detach=false ${IMG_NAME} /bin/bash -c "bash"

run-detached:
	docker-compose up -d web worker

provision:
	docker-compose run --no-deps provision python3 -m boptest_submit ./testcases/${TESTCASE}

stop:
	docker-compose down

compile_testcase:
	(cd testing && make compile_testcase_model TESTCASE=${TESTCASE})

.PHONY: build run run-detached remove-image stop provision
