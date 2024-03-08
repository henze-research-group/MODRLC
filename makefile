# Build the Docker images using docker-compose.
# This command reads the docker-compose.yml file and builds images for the services defined there.
# It's useful for ensuring that your Docker images are ready and up-to-date with your application's requirements.
# This is a standard step in deploying Dockerized applications.
#
# *Optimizing Build Time with Cache*: Docker uses a layer-based caching system. If
# you haven't changed any layers in your Dockerfile since the last build, Docker will 
# use the cached layers, which significantly speeds up the build process. In this case, 
# running docker-compose build again won't take much time and can assure you that your setup is still working as expected.

build:
	docker-compose build

# Build the Docker images without using cache.
# The `--no-cache` flag forces the build process to not use the cache when building the image.
# This is useful when you want to ensure that your images are completely fresh, with no layers reused from previous builds.
# It's often used to troubleshoot issues caused by dependencies or data persisting in cached layers.
build-nocache:
	docker-compose build --no-cache

# Remove the specified Docker image using docker-compose.
# The `rm` command is used to remove stopped service containers.
# The `-sf` flags imply stopping the containers if they are running (`-s`) and force removal without confirmation (`-f`).
# This command is typically used to clean up containers that are no longer needed, freeing up system resources.
remove-image:
	docker-compose rm -sf

# Start multiple service instances in detached mode and then provision them.
# `run-many-detached` starts multiple instances of the `worker` service along with the `web` service.
# `provision` then runs a specific Python script inside the `provision` service container.
# The `docker-compose logs -f` command is used to follow the logs of the `web` and `worker` services.
# This command is useful for scaling your application horizontally by running multiple instances of a service.
run-many :
	$(MAKE) run-many-detached
	$(MAKE) provision
	docker-compose logs -f web worker

# Start services in detached mode, provision them, and follow logs.
# `run-detached` starts the `web` and `worker` services in detached mode.
# `provision` runs a provisioning script, useful for initial setup tasks.
# `docker-compose logs -f` tails the logs of `web` and `worker`, useful for monitoring the services.
# This command is typically used for running your application in the background while still being able to monitor its output.
run :
	$(MAKE) run-detached
	$(MAKE) provision
	docker-compose logs -f web worker

# Open a Bash shell in the Docker container.
# `$(COMMAND_RUN)` is likely a variable defined elsewhere in your Makefile specifying how to run commands.
# `--detach=false` ensures the command runs in the foreground.
# `${IMG_NAME}` is a variable representing the name of the Docker image.
# This command is useful for debugging or managing the application within the container.
bash:
	$(COMMAND_RUN) --detach=false ${IMG_NAME} /bin/bash -c "bash"

# Start specified services in detached mode.
# `docker-compose up -d` starts the services defined in the docker-compose.yml file in detached mode.
# `web` and `worker` are the names of the services being started.
# This command is used to run services in the background, freeing up the terminal.
run-detached:
	docker-compose up -d web worker

# Start multiple instances of a service in detached mode.
# `--scale worker=${NUM}` starts a specified number
# (`${NUM}`) of instances of the `worker` service, along with the `web` service.
# The `-d` flag indicates detached mode, running them in the background.
# This command is particularly useful for testing the scalability and load balancing of your application.
run-many-detached:
	docker-compose up -d --scale worker=${NUM} web

# Provision the application.
# This command runs a specific Python module (`boptest_submit`) in the `provision` service.
# `--no-deps` ensures that no linked service is started.
# The `./testcases/${TESTCASE}` argument specifies the testcase to be used with the script.
# This is commonly used for setting up or configuring the application, particularly in complex setups or multi-service environments.
provision:
	docker-compose run --no-deps provision python3 -m boptest_submit ./testcases/${TESTCASE}

# Stop and remove Docker containers, networks, images, and volumes.
# `docker-compose down` stops the running containers and removes them along with their networks, images, and optionally, volumes.
# This command is essential for cleanly shutting down your Dockerized environment and ensuring no residual resources are left.
stop:
	docker-compose down

# Compile a specific testcase.
# This command changes directory to `testing` and runs a Makefile target `compile_testcase_model` with the `TESTCASE` variable.
# It's specifically used for compiling a testcase, which is part of the larger build process.
# This is useful for projects that need to compile or prepare test cases as part of their development or deployment process.
compile_testcase:
	(cd testing && make compile_testcase_model TESTCASE=${TESTCASE})

# Declare phony targets.
# `.PHONY` is used to explicitly declare targets that do not represent files.
# This prevents make from getting confused by files of the same name and ensures these targets are always executed.
.PHONY: build run run-detached remove-image stop provision
