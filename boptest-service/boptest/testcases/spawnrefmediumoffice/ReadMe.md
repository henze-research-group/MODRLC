#Medium Office Building - Spawn

This is a 15-zone building with 3 variable air volume multi-zone AHUs.

## Under development

This model is currently under development. If you attempt to compile or simulate it, the process will return an error. 
You can, if you wish, open the `.mo` files found in the `models/` directory with the Modelica editor of your choice to see the 
usage of Spawn and SignalExchange blocks.

##Structure


- ``doc/`` contains documentation of the test case. It includes a list of sensor and control override points for external controllers.
- ``models/`` contains the model files for the test case.
- ``config.py`` defines the configuration of the test case for building the Docker image.

##Usage


Build the Docker container. At the root of the ACTB, open a terminal and use:
``make build TESTCASE=spawnrefmediumoffice``
Then, run the Docker container:
``make run TESTCASE=spawnrefmediumoffice``
You can now interact with the model using the Python API (e.g. initialize and step the simulation, read sensors and override controls, etc.).
See the `{actb root}/examples/python` folder for example controllers (rule-based, model predictive and reinforcement learning controls). 

##Compile the Model

Recompiling the model is not normally needed. However, should you need to modify the `models/spawnrefmediumoffice.mo` file, you should follow these steps to recompile the model.

1. `cd` to `{actb root}/testing`
2. Build the Docker container used for compiling the model using `make build-jm`
3. Compile the model using `make compile_testcase_model TESTCASE=spawnrefmediumoffice`
4. `cd` back to the ACTB root
5. Re-build the Docker container used for simulating models using `make build TESTCASE=spawnrefmediumoffice`
