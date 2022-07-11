#Simulating multi-building scenarios

By default, the ACTB is launched with a single simulation worker which is able to simulate one building at a time.
However, users can launch the ACTB with several simulation workers, allowing the simulation of multiple buildings at the same time.

To do so, instead of launching the ACTB using `make run`, you can launch it using `make run-many NUM=<number of workers>`.
The ACTB, using the underlying tools inherited from Alfalfa, will manage the workers so that simulation jobs will be automatically queued
and distributed among workers.
This means that if 3 workers are running, and 3 simulation jobs are requested, all can be run at the same time. However, 
should you try to run 4 jobs on only 3 workers, then 3 jobs will be run at the same time and the last one will be run only 
after one worker will have completed its simulation.
Hence, please carefully select the number of workers, taking into account the type of simulation you want to run and the
capabilities of your computer.

#Usage

Please refer to the example shown in `3SmallOffices.py`, which shows how to run 3 Small Office models simultaneously.

As you will see in the example, the ACTB client uses a new class called `Portfolio` to manage several simulations. This class
needs a definition of the various buildings you want to simulate in the form of a Python dictionary, shown and commented in the example.
In this dictionary, you will define:
- a unique identifier for each building. This can be any Python string. In the example, the buildings are named `fist`, `second` and `third`.
- for each building, you will need to define: 
  - the type of building, as found in the `testcases` folder. In this example, we are using the `spawnrefsmalloffice` model.
  - the initialization parameters, `start_time` and `warmup_period`, as with any ACTB test case
  - the forecasting parameters, `horizon` and `interval`
  - the simulation time step. It will be identical across all buildings for synchronous simulation.
  - whether or not you wish to use a metamodel instead of Spawn models. If not, use `None`. If yes, use the metamodel 
  ID (usually, the same as the test case name).

Once the building portfolio has been defined, and the client launched using the `Portfolio` class, you can initialize
all test cases using the `initialize_all()` method.

To control the simulation (stepping, requesting KPIs or forecasts, etc.) you can use the same methods as for the "classic"
ACTB client, except that you will need to pass an additional argument, `id`, which contains the unique building identifier.
For example, instead of using `advance(control_u=<your control vector>)` as in the "classic" client, you will now use
`advance(id=<unique building identifier>, control_u=<your control vector>`. This applies to all methods initially available in the "classic" client.
Note: currently, only the `advance`, `kpis` and `results` methods have been implemented. 