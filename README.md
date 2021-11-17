# IBPSA Project 1 - BOPTEST

[![Build Status](https://travis-ci.com/ibpsa/project1-boptest.svg?branch=master)](https://travis-ci.com/ibpsa/project1-boptest)

Building Optimization Performance Tests

This repository contains prototype code for the Building Optimization Performance Test framework (BOPTEST)
that is being developed as part of the IBPSA Project 1 (https://ibpsa.github.io/project1/).

## Structure
- ``/testcases`` contains test cases, including docs, models, and configuration settings.
- ``/examples`` contains prototype code for interacting with a test case and running example tests with simple controllers.  Those controllers are implemented in both Python (Version 2.7) and Julia (Version 1.0.3).
- ``/parsing`` contains prototype code for a script that parses a Modelica model using signal exchange blocks and outputs a wrapper FMU and KPI json.
- ``/template`` contains template Modelica code for a test case emulator model.
- ``/testing`` contains code for unit and functional testing of this software.  See the README there for more information about running these tests.
- ``/data`` contains prototype code for generating and managing data associated with test cases.  This includes boundary conditions, such as weather, schedules, and energy prices, as well as a map of test case FMU outputs needed to calculate KPIs.
- ``/forecast`` contains prototype code for returning boundary condition forecast, such as weather, schedules, and energy prices.
- ``/kpis`` contains prototype code for calculating key performance indicators.
- ``/docs`` contains design requirements and guide documentation.

## Quick-Start to Run Test Cases
1) Install [Docker](https://docs.docker.com/get-docker/).
2) Build the test case by ``$ make build TESTCASE=<testcase_dir_name>`` where <testcase_dir_name> is the name of the test case subdirectory located in ``/testcases``.
3) Deploy the test case by ``$ make run TESTCASE=<testcase_dir_name>`` where <testcase_dir_name> is the name of the test case subdirectory located in ``/testcases``.
4) In a separate process, use the test case API defined below to interact with the test case using your test controller.  Alternatively, view and run an example test controller as described in the next step.
5) Run an example test controller:

* For Python-based example controllers:
  * Add the root directory of the BOPTEST repository to the PYTHONPATH environment variable.
  * Build and deploy ``testcase1``.  Then, in a separate terminal, use ``$ cd examples/python/ && python testcase1.py`` to test a simple proportional feedback controller on this test case over a two-day period.
  * Build and deploy ``testcase2``.  Then, in a separate terminal, use ``$ cd examples/python/ && python testcase2.py`` to test a simple supervisory controller on this test case over a two-day period.

* For Julia-based example controllers:
  * Build and deploy ``testcase1``.  Then, in a separate terminal, use ``$ cd examples/julia && make build Script=testcase1 && make run Script=testcase1`` to test a simple proportional feedback controller on this test case over a two-day period.  Note that the Julia-based controller is run in a separate Docker container.
  * Build and deploy ``testcase2``.  Then, in a separate terminal, use ``$ cd examples/julia && make build Script=testcase2 && make run Script=testcase2`` to test a simple supervisory controller on this test case over a two-day period.  Note that the Julia-based controller is run in a separate Docker container.
  * Once either test is done, use ``$ make remove-image Script=testcase1`` or ``$ make remove-image Script=testcase2`` to removes containers, networks, volumes, and images associated with these Julia-based examples.

6) Shutdown a test case container by selecting the container terminal window, ``Ctrl+C`` to close port, and ``Ctrl+D`` to exit the Docker container.
7) Remove the test case Docker image by ``$ make remove-image TESTCASE=<testcase_dir_name>``.

## Test Case RESTful API
- To interact with a deployed test case, use the API defined in the table below by sending RESTful requests to: ``http://127.0.0.1:5000/<request>``

Example RESTful interaction:

- Receive a list of available measurement names and their metadata: ``$ curl http://127.0.0.1:5000/measurements``
- Receive a forecast of boundary condition data: ``$ curl http://127.0.0.1:5000/forecast``
- Advance simulation of test case 2 with new heating and cooling temperature setpoints: ``$ curl http://127.0.0.1:5000/advance -d '{"oveTSetRooHea_u":293.15,"oveTSetRooHea_activate":1, "oveTSetRooCoo_activate":1,"oveTSetRooCoo_u":298.15}' -H "Content-Type: application/json"``.  Leave an empty json to advance the simulation using the setpoints embedded in the model.

| Interaction                                                           | Request                                                   |
|-----------------------------------------------------------------------|-----------------------------------------------------------|
| Advance simulation with control input and receive measurements        |  POST ``advance`` with json data "{<input_name>:<value>}" |
| Initialize simulation to a start time using a warmup period in seconds     |  PUT ``initialize`` with arguments ``start_time=<value>``, ``warmup_time=<value>``|
| Receive communication step in seconds                                 |  GET ``step``                                             |
| Set communication step in seconds                                     |  PUT ``step`` with argument ``step=<value>``              |
| Receive sensor signal names (y) and metadata                          |  GET ``measurements``                                     |
| Receive control signals names (u) and metadata                        |  GET ``inputs``                                           |
| Receive test result data                                              |  GET ``results``                                          |
| Receive test KPIs                                                     |  GET ``kpi``                                              |
| Receive test case name                                                |  GET ``name``                                             |
| Receive boundary condition forecast from current communication step   |  GET ``forecast``                                         |
| Receive boundary condition forecast parameters in seconds             |  GET ``forecast_parameters``                              |
| Set boundary condition forecast parameters in seconds                 |  PUT ``forecast_parameters`` with arguments ``horizon=<value>``, ``interval=<value>``|
| Receive current test scenario                                         |  GET ``scenario``                                   |
| Set test scenario  		                                             |  PUT ``scenario`` with arguments ``electricity_price=<'constant' or 'dynamic' or 'highly_dynamic'>``|

## Development

This repository uses pre-commit to ensure that the files meet standard formatting conventions (such as line spacing, layout, etc).
Presently only a handful of checks are enabled and will expanded in the near future. To run pre-commit first install
pre-commit into your Python version using pip `pip install pre-commit`. Pre-commit can either be manually by calling
`pre-commit run --all-files` from within the BOPTEST checkout directory, or you can install pre-commit to be run automatically
as a hook on all commits by calling `pre-commit install` in the root directory of the BOPTEST GitHub checkout.

## Gym Interface
The gym interface works after building the docker container for the selected Spawn model. The gym environment can be customized to form various control problems by initializing  the environment with different settings to setup different problems. 
 
### Initializating the Environment 

The following instance variables are available: <br>
* ``Ts`` = Time step in seconds, (*default*=300)
* ``episode_length`` = Simulation time in seconds, (*default*=300)
* ``start_time`` = Start time of simulation from the start of a year, (*default*=0)
* ``actions`` = Select which control actions to take, (*default*=300)
* ``KPI_rewards`` = Set the weights for the different KPIs in a dictionary format to form the reward function, (*default*= energy and thermal discomfort set to -1, others set to 0). See the example provided below. 
* ``kpi_zones`` = Form the reward function from the selected zones, (*default*= ["1","2"])
* ``building_obs`` = Can Specify which building sensors as well as time variable to return as observation (*default*= hour of the day, Zone 1 and Zone 2 temperature)
* ``forecast_obs`` = Select which exogeneous weather variables and its forecasts to observe, (*default*= Current Outside air temperature and Global Horizontal Irradiation )
* ``lower_obs_bounds`` = Manually provide the observation state lower bounds in a list format, (*default* = [0, 243.15,243.15,243.15,0])
* ``upper_obs_bounds`` = Manually provide the observation state upper bounds in a list format, (*default*= [24, 323.15,243.15,243.15,1000])
* ``n_obs`` = This normalizes the observation states between the upper and lower bounds if set to True, (*default*= False)
* ``password`` = Provide your own password, (*default*=None)
* ``DR_event`` = To do DR events set this to True, (*default*=False)
* ``dr_obs`` = To do DR events set this to True, (*default*=False)
* ``DR_time`` = Set the time interval for th DR in a list format, (*default*=[3600x14,3600x14])
* ``dr_power_limit`` = Set the time interval for th DR in a list format, (*default*=[3600x14,3600x14])
 
 
 ### Functionalities of the Gym Environment
 
The following instance variables are available: <br>
* ``env.reset()`` = Time step in seconds, (*default*=300)
* ``env.step()`` = Time step in seconds, (*default*=300)
* ``env.get_KPIs()`` = Time step in seconds, (*default*=300)
* ``env.get_building_states()`` = Time step in seconds, (*default*=300)
* ``env.get_input_hist()`` = Time step in seconds, (*default*=300)
* ``env.get_info()`` = Time step in seconds, (*default*=300)


 Example: 
 
 ```
 ''' Code shows an example to setup a control problem for the small office building '''
 
 env = BoptestGymEnv(Ts=300,                                                                    # Select time step (5 minute is selected)
                     start_time = 3*3600*24,                                                    # Select start of simulation (Here it starts from Jan 4th - midnight)
                     episode_length = 3600*24,                                                  # Select length of simulation (Day simulation is selected) 
                     actions = ['PSZACcontroller_oveHeaPer1_u','PSZACcontroller_oveHeaPer2_u'], # Select which actions to control (Zone 1 and Zone 2 Low-level heating coils)
                     KPI_rewards = {
                        "ener_tot": {"hyper": -1, "power": 1},
                        "tdis_tot": {"hyper": -1, "power": 1},
                        "idis_tot": {"hyper": 0, "power": 1},
                        "cost_tot": {"hyper": 0, "power": 1},
                        "emis_tot": {"hyper": 0, "power": 1},
                        "power_pen":{"hyper": 0, "power":1}}
                                         ) 
 ```


## Proposed Interface Design
A proposed BOPTEST home page and interface for creating accounts and sharing results is published here https://xd.adobe.com/view/0e0c63d4-3916-40a9-5e5c-cc03f853f40a-783d/.

## Publications
D. Blum, F. Jorissen, S. Huang, Y. Chen, J. Arroyo, K. Benne, Y. Li, V. Gavan, L. Rivalin, L. Helsen, D. Vrabie, M. Wetter, and M. Sofos. (2019). “Prototyping the BOPTEST framework for simulation-based testing of advanced control strategies in buildings.” In *Proc. of the 16th International Conference of IBPSA*, Sep 2 – 4. Rome, Italy.

# MODRLC
