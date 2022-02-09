# Rule-based controller examples:

This folder contains three examples of a rule-based controller for the Spawn Reference Small Office test case.

``supervisory_example.py`` is an example of supervisory control which overrides the heating and cooling setpoints
during a heating day.

``lowlevel_example.py`` is an example of low-level control during a heating day.

``no_override.py`` simply simulates the Spawn model using the built-in rule-based controller.

## Usage:

### Quick start:

- open a terminal window, and ``cd`` to the root directory
- run ``sudo make run TESTCASE=spawnrefsmalloffice``
- in a new terminal window, ``cd`` to this directory and run the controller script of your choice:
  - ``python supervisory_example.py``
  - ``python lowlevel_example.py``
  - ``python no_override.py``

### Detailed usage:

First, import the rbc library:
```
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'rulebased'))
from rbc import rulebased
```

Then, import the configuration file to set the current scenario (see the next section detailing its usage):

``import config``

Set up the simulation parameters:

```
start_time = 0                  # in seconds from January 1st, 00:00:00
warmup = 0                      # simulation warm-up days
length = 24 * 3600 * 1          # simulation length in seconds
step = 300                      # simulation step in seconds
control_level = 'supervisory'   #either 'lowlevel' or 'supervisory'
```

Instantiate the rule-based controller:

``rbc = rulebased(config = config, step = step, level = control_level, start_time = start_time)``
See the readme file in ``interfaces/rulebased`` for more details on the rule-based controller class.

Initialize the result to None (TODO: fix this):

``res = None``

Set up the simulation loop, and use the apply_control method to step the simulation using the setpoints specified in
the ``config.py`` file:

```
for i in range(int(length/step)):
    res = rbc.apply_control(res)
```

Finally, retrieve the results and KPIs at the end of the simulation:

```
final_results = rbc.get_results()
final_kpis = rbc.get_kpis()
print(final_kpis)
```

### Scenario configuration:

The Spawn test case configuration file ``config.py`` contains schedules, sensor and override points as reported in the 
test case documentation. It is used by the rule-based library found in ``/interfaces/rulebased``.
It is used for:
- identifying sensors and overrides (low-level and supervisory) available in the Spawn test case
- specifying occupancy schedules
- specifying demand-limit scenarios
- specifying controlled zones
