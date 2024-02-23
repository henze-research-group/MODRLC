
build:
	docker-compose build

build-nocache:
	docker-compose build --no-cache

remove-image:
	docker-compose rm -sf

run-many :
	$(MAKE) run-many-detached
	$(MAKE) provision
	docker-compose logs -f web worker

run :
	$(MAKE) run-detached
	$(MAKE) provision
	docker-compose logs -f web worker

bash:
	$(COMMAND_RUN) --detach=false ${IMG_NAME} /bin/bash -c "bash"

run-detached:
	docker-compose up -d web worker

run-many-detached:
	docker-compose up -d --scale worker=${NUM} web

provision:
	docker-compose run --no-deps provision python3 -m boptest_submit ./testcases/${TESTCASE}

stop:
	docker-compose down

compile_testcase:
	(cd boptest-service/boptest/testing && make compile_testcase_model TESTCASE=${TESTCASE})

.PHONY: build run run-detached remove-image stop provision
