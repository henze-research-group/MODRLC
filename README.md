# Advanced Controls Test Bed

The Advanced Controls Test Bed (ACTB) is a virtual buildings test bed that interfaces external controllers to high-fidelity Spawn of EnergyPlus models. 
The ACTB has two interfaces to Python control libraries:
- one interface for model predictive controllers (MPC) based on [do-mpc](https://www.do-mpc.com/en/latest/)
- one interface for reinforcement learning controllers (RLC) based on [OpenAI Gym](https://gym.openai.com/)

[Spawn of EnergyPlus](https://www.energy.gov/eere/buildings/downloads/spawn-energyplus-spawn) is a model-exchange framework that allows the simulation of building envelope and internal gains models in EnergyPlus, and their HVAC systems and controls in Modelica.

This makes the ACTB a flexible and user-friendly framework for developing and evaluating advanced controls using high-fidelity building models.

The ACTB is based on the BOPTEST framework available [here](https://github.com/ibpsa/project1-boptest) and the [BOPTEST OpenAI Gym interface](https://github.com/ibpsa/project1-boptest-gym).

The ACTB is currently in its first release version and might undergo changes, contain broken modules, or function unexpectedly. Please report all issues in the Issues tab at the top of the page.

## Install

### Operating systems

The ACTB works with Linux and macOS out of the box, but requires an additional software layer for working on Windows. If you are a Windows user,
please install the **Windows Subsystem for Linux (WSL)** by following the instructions [here](https://docs.microsoft.com/en-us/windows/wsl/install).
You will simply need to start an instance of the WSL first, then run the commands found in the various instructions of this repository in the Linux terminal
that will be launched.

### Docker

The ACTB is packaged as a Docker container, please install Docker by following the instructions [here](https://docs.docker.com/get-docker/).

### Python

While the Docker container comes with Python and all the dependencies installed, if you are running a controller script externally
you will need to install Python and a few libraries. For Python, please install **Python 3.6** by following these links for [Linux](https://docs.python-guide.org/starting/install3/linux/),
[macOS](https://docs.python-guide.org/starting/install3/osx/), or [Windows](https://docs.python.org/3/using/windows.html).

Note: If you have several versions of Python installed, make sure you are running Python 3.6 by replacing `python` 
commands with `python3` whenever the command is present in the instructions.

### Libraries

We strongly recommend installing and using `pip` to manage Python libraries.
Follow the instructions [here](https://pip.pypa.io/en/stable/installation/) to install pip.

With pip installed, just open a terminal window, `cd` at the root of the ACTB
and run:

`pip install -r requirements.txt`

If you have several versions of Python installed, you may need to replace `pip` by `pip3` in the above command to make sure you 
are installing these libraries for your Python 3. 

## Quick-Start to Run Test Cases

1. Make sure the Docker daemon is running. 
2. Build the Docker containers by running ``$ make build``
3. Run the Docker containers by running ``$ make run``
4. Run an example test controller in a separate terminal:

  * ``$ cd examples/python/Single-zone/MPC-spawnrefsmalloffice && python main.py`` to test a MPC controller.
  * ``$ cd examples/python/Single-zone/RLC-spawnrefsmalloffice && python DQN_Test_run.py`` to test a RLC controller.
  * ``$ cd examples/python/Single-zone/RBC-spawnrefsmalloffice && python supervisory_example.py`` to test the RBC controller.
 
4. Shutdown a test case container by selecting the container terminal window, ``Ctrl+C`` to close port, and ``make stop`` to stop the Docker container.
5. Remove the test case Docker image by ``$ make remove-image``.

Please refer to the ReadMe file present in the ```actb_client``` directory for more details on the API usage.

## Architecture

The ACTB is based on BOPTEST-service, a merge between BOPTEST and [Alfalfa](https://github.com/NREL/alfalfa). It is supplemented by a library of high-fidelity Spawn models and two advanced controller interfaces. A metamodeling framework allows the generation of reduced order models from Spawn data, in order to provide computationally-efficient models for MPC planning models and RLC pre-training (see the RLC guide [here](TODO)).

![ACTB architecture](docs/figures/ACTBarchi.png)
## Interfaces

Two advanced controller interfaces are currently available for the ACTB.
- the do-mpc interface for MPC is available under ``/interfaces/dompc``, along with a ReadMe file and examples of applications. It is used by the MPC example found in ``/examples/python/MPC-spawnrefsmalloffice``.
- the OpenAI Gym interface for RLC is available under ``/interfaces/openai-gym``, along with a ReadMe file and examples of applications. It is used by the RLC example found in ``/examples/python/RLC-spawnrefsmalloffice``

## Test cases

Testcases are found in the ``/testcases`` directory. Example controllers to go with these test cases are found under the ``/examples`` directory.

For the moment, one Spawn test case is available. It represents the U.S. Department of Energy's Small Office Building.
It is provided with a documentation, found under ``/testcases/spawnrefsmalloffice/docs``.

![Animation of the ACTB test case](docs/figures/ACTBdemo.gif)

## Known Issues

Currently, the ACTB has some issues that we are aware of and are working towards solving. These are:
- on first startup of the Docker container, the container might hang or even run a simulation without user 
input. While this issue is being investigated, just CTRL+C then `make stop` to stop the container, 
then restart it with `make run`. Upon second startup, the container will behave as expected.

## Structure
- ``/testcases`` contains Spawn of EnergyPlus test cases, including docs, models, and configuration settings.
- ``/examples`` contains examples of MPC and RLC Python controllers that interact with Spawn models.
- ``/interfaces`` contains the clients for interfacing do-mpc and OpenAI Gym to the ACTB
- ``/metamodeling`` contains prototype code for the metamodeling framework
- ``/parsing`` contains prototype code for a script that parses a Modelica model using signal exchange blocks and outputs a wrapper FMU and KPI json.
- ``/template`` contains template Modelica code for a test case emulator model.
- ``/testing`` contains code for unit and functional testing of this software.  See the README there for more information about running these tests.
- ``/data`` contains prototype code for generating and managing data associated with test cases.  This includes boundary conditions, such as weather, schedules, and energy prices, as well as a map of test case FMU outputs needed to calculate KPIs.
- ``/forecast`` contains prototype code for returning boundary condition forecast, such as weather, schedules, and energy prices.
- ``/kpis`` contains prototype code for calculating key performance indicators.
- ``/docs`` contains design requirements and guide documentation.

## Acknowledgements
We gratefully acknowledge funding by the U.S. Department of Energy under Project 3.2.6.80, titled _Multi-Objective Deep Reinforcement Learning Controls_.

To develop the ACTB, we rely on the following software:
- the [Buildings Operation Performance TEST](https://github.com/ibpsa/project1-boptest), developed under IBPSA Project 1
- the [BOPTEST OpenAI Gym interface](https://github.com/ibpsa/project1-boptest-gym), developed under IBPSA Project 1
- [Spawn of EnergyPlus](https://www.energy.gov/eere/buildings/downloads/spawn-energyplus-spawn)
- the [System Identification Package for Python](https://github.com/CPCLAB-UNIPI/SIPPY.git)
- the [do-mpc](https://www.do-mpc.com/en/latest/) package
- the [OpenAI Gym](https://gym.openai.com/) package

## Authors
This project is led by Professor Gregor Henze, at the University of Colorado Boulder.
It is developed and maintained by Dr. Thibault Marzullo, Sourav Dey, and Nicholas Long, at the University of Colorado Boulder.

Former project members:
- Developer (2021-2021): José Angel Leiva Vilaplana, Masters candidate, Universitat Politecnica de Catalunya.
