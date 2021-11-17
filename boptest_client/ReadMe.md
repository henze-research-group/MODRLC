TODO: Update with API calls, not RESTful requests.

# Test Case RESTful API
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
