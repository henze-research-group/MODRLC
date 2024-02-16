# Utility Functions
###############################################################################

IMG_NAME=jm

COMMAND_RUN=docker run \
	  --name ${IMG_NAME} \
	  --detach=true \
	  --rm \
	  -it \
	  ${IMG_NAME}

build_jm_image:
	docker build --no-cache --rm -t ${IMG_NAME} .

remove_jm_image:
	docker rmi ${IMG_NAME}

run_jm:
	$(COMMAND_RUN)
	docker cp ../boptest-service/boptest/testing/ ${IMG_NAME}:/usr/local/testing

copy_to_jm:
	docker cp ../${ARGS} ${IMG_NAME}:/usr/local/testing
	docker exec -it ${IMG_NAME} /bin/bash -c "sudo chown -R developer: /usr/local/testing && exit"

copy_testcase_to_jm:
	make copy_to_jm ARGS=testcases/${TESTCASE}
	docker cp ../testcase.py ${IMG_NAME}:/usr/local/testing/${TESTCASE}
	docker cp ../version.txt ${IMG_NAME}:/usr/local/testing/${TESTCASE}
	make exec_jm ARGS="touch ${TESTCASE}/__init__.py"

copy_from_jm:
	docker cp ${IMG_NAME}:/usr/local/testing/${ARGS} ../${ARGS}

copy_testcase_from_jm:
	docker cp ${IMG_NAME}:/usr/local/testing/${ARGS} ../testcases/${ARGS}

exec_jm:
	docker exec -it ${IMG_NAME} /bin/bash -c "cd /usr/local/testing && ${ARGS} && exit"

bash:
	docker exec -it ${IMG_NAME} /bin/bash -c "cd / && /bin/bash && exit"

stop_jm:
	docker stop ${IMG_NAME}
# Make sure jm image stops being used
#python sleep10.py

compile_testcase_model:
	-make stop_jm
	python3 ../spawn-tools/generate_spawndata.py ${TESTCASE}
	(cd ../testcases/SpawnResources/${TESTCASE}/ && cp dataFromModel.csv emissions.csv prices.csv weather.csv ../../${TESTCASE}/models/Resources/)
	make run_jm
	make copy_to_jm ARGS=boptest-service/boptest/parsing
	make copy_to_jm ARGS=boptest-service/boptest/data
	make copy_to_jm ARGS=testcases/${TESTCASE}
	docker cp ../testcases/SpawnResources/ ${IMG_NAME}:/
#docker cp Routing.mo ${IMG_NAME}:/home/developer/MODELICAPATH/Modelica/Blocks/
#docker cp Interfaces.mo ${IMG_NAME}:/home/developer/MODELICAPATH/Modelica/Blocks/
	make exec_jm ARGS="python set_library_versions.py ${TESTCASE} && cd ${TESTCASE}/models && python compile_fmu.py"
	make copy_testcase_from_jm ARGS=${TESTCASE}/models/wrapped.fmu
	make copy_testcase_from_jm ARGS=${TESTCASE}/models/wrapped.mo
	make stop_jm

generate_testcase_data:
	make run_jm
	make copy_to_jm ARGS=boptest-service/boptest/parsing
	make copy_to_jm ARGS=boptest-service/boptest/data
	make copy_to_jm ARGS=testcases/${TESTCASE}
	make exec_jm ARGS="cd ${TESTCASE}/models && python generate_data.py"
	docker cp ${IMG_NAME}:/usr/local/testing/testcases/${TESTCASE}/models/Resources ../testcases/${TESTCASE}/models/
	make stop_jm
	