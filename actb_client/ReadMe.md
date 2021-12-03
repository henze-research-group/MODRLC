# Test Case RESTful API
To interact with a deployed test case, use the API defined in the table below for sending RESTful requests to ```http://localhost:80``` by default.

First, initialize the client. For example, you could do:
```
from actb_client import ActbClient
url = 'http://localhost:80'
client = ActbClient(url)
```
You can now interact with the client. First, select a testcase, then send the initialization command. Finally, you can step through the simulation.
```
num_steps = 10
client.select('spawnrefsmalloffice')
client.initialize({<your init parameters>})

for i in range(num_steps):
    client.advance(control_u={<your control vector>})
results = client.result()
...
```

| Interaction                                                           | API call                                                  |
|-----------------------------------------------------------------------|-----------------------------------------------------------|
|Select the test case. Note: it must have been built and submitted first.| select(testcase) with testcase a string corresponding to the name of the folder containing the testcase. Ex: ```spawnrefsmalloffice```|
| Advance simulation with control input and receive measurements        |  advance(control_u) with control_u = {<input_name>:<value>}" |
| Initialize simulation to a start time using a warmup period in seconds     |  initialize(**args) with arguments ``start_time=<value>``, ``warmup_time=<value>``|
| Receive communication step in seconds                                 |  get_step()                                             |
| Set communication step in seconds                                     |  set_step(step)              |
| Receive sensor signal names (y) and metadata                          |  measurements()                                     |
| Receive control signals names (u) and metadata                        |  inputs()                                           |
| Receive test result data                                              |  results()                                         |
| Receive test KPIs                                                     |  kpis()                                             |
| Receive test case name                                                |  name()                                            |
| Receive boundary condition forecast from current communication step   |  get_forecasts()                                        |
| Receive boundary condition forecast parameters in seconds             |  get_forecast_parameters()                              |
| Set boundary condition forecast parameters in seconds                 |  set_forecast_parameters(horizon, interval) |
| Receive current test scenario                                         |  get_scenario()                                   |
| Set test scenario  		                                             |  set_scenario(arg) with argument ``'constant' or 'dynamic' or 'highly_dynamic'``|
