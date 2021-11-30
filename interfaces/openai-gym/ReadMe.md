## Gym Interface
The gym interface works after building the docker container for the selected Spawn model. The gym environment can be customized to form various control problems by initializing  the environment with different settings to setup different problems. 
 
### Initializating the Environment 

The following instance variables are available.: <br>
* ``Ts`` = Time step in seconds, (*default*=300)
* ``episode_length`` = Simulation time in seconds, (*default*=300)
* ``start_time`` = Start time of simulation from the start of a year, (*default*=0)
* ``actions`` = Select which control actions to take, (*default*= Low-level heating coil controls for Zone 1 and Zone 2)
* ``KPI_rewards`` = Set the weights for the different KPIs in a dictionary format to form the reward function, (*default*= energy and thermal discomfort set to -1, others set to 0). See the example provided below. 
* ``kpi_zones`` = Form the reward function from the selected zones, (*default*= ["1","2"])
* ``building_obs`` = Can Specify which building sensors as well as time variable to return as observation (*default*= hour of the day, Zone 1 and Zone 2 temperature)
* ``forecast_obs`` = Select which exogeneous weather variables and its forecasts to observe, (*default*= Current Outside air temperature and Global Horizontal Irradiation )
* ``lower_obs_bounds`` = Manually provide the observation state lower bounds in a list format, (*default* = [0, 243.15,243.15,243.15,0])
* ``upper_obs_bounds`` = Manually provide the observation state upper bounds in a list format, (*default*= [24, 323.15,323.15,323.15,1000])
* ``n_obs`` = This normalizes the observation states between the upper and lower bounds if set to True, (*default*= False)
* ``password`` = Provide your own password, (*default*=None)
* ``DR_event`` = To do DR events set this to True, (*default*=False)
* ``dr_obs`` = List to indicate the type of binary signals to check whether there is current DR event going on or some hours ahead. This is only used if ``DR_event`` is set to True.  (*default*=[0,1])
* ``DR_time`` = Set the time interval for th DR event in a list format, (*default*=[3600x14,3600x16] an event between 2 p.m. and 4 p.m.)
* ``dr_power_limit`` = Set the power limit penalty term. If the total power is above this limit there is penalty. This is mulitplied by the penalty weight set in ``KPI_rewards``. (*default*=10000)
 
 
 ### Functionalities of the Gym Environment
 
The following instance variables are available: <br>
* ``env.reset()`` : Restart the simulation to the start
* ``env.step(u)`` : Advance one time step of simulation. ``u`` is the list of the control vector containing the values of only the selected controlled actions. This returns the observation ``states``, the ``reward``, the ``done`` flag and ``info``
* ``env.get_KPIs()`` : Returns the different KPIs calculated by the BOPTEST framework in a dictionary format.
* ``env.get_weather_forecast()`` : Returns a dictionary of the weather variables with its forecast.
* ``env.get_building_states()`` : Returns a dictionary of all the building sensors available in the model.
* ``env.change_rewards_weights(KPI_rewards)`` : This enables to change the weights during a simulation. The format to ``KPI_rewards`` is similar to the one used in the environment initialization.
* ``env.set_DR_time(DR_time)`` : This enables to change the DR time in a day during a simulation. The format to ``DR_time`` is similar to the one used in the environment initialization.
* ``env.get_input_hist()`` : This returns the full control vector including the activated and the deactivated controls. 
* ``env.get_info()`` : This returns the dictionary of all the individual rewards from the individual zones. This is particularly useful for a multi-agent setting. 


 Example: 
 
 ```
 ''' Code shows an example to setup a control problem for the small office building '''
 
 env = BoptestGymEnv(Ts=300,                                                                    # Select time step (5 minute is selected)
                     start_time = 3*3600*24,                                                    # Select start of simulation (Here it starts from Jan 4th - midnight)
                     episode_length = 3600*24,                                                  # Select length of simulation (Day simulation is selected) 
                     actions = ['PSZACcontroller_oveHeaPer1_u','PSZACcontroller_oveHeaPer2_u'], # Select which actions to control (Zone 1 and Zone 2 Low-level heating coils)
                     building_obs = ['senHouDec_y','senTemRoom1_y','senTemRoom2_y'],            # Specify which building sensor states to return as observation States
                     forecast_obs = [{'TDryBul':[0,1],'HGloHor':[0]}],                          # Specify which exogenous states to return as observation States - 0: index means current, 1: index means forecasted state 1 hour ahead
                     lower_obs_bounds = [ 0, 243.15, 243.15, 243.15, 243.15,   0],              # manually set the lower bounds for observation
                     upper_obs_bounds = [ 0, 313.15, 313.15, 313.15, 313.15, 700],              # manually set the upper bounds for observation
                     kpi_zones = ["1","2"],                                                     # Only Zone 1 and Zone 2 KPIs are used to form the reward function
                     n_obs = True,                                                              # If set to True returns a normalized state vector between (0-1)
                     KPI_rewards = {
                        "ener_tot": {"hyper": -1, "power": 1},
                        "tdis_tot": {"hyper": -1, "power": 1},
                        "idis_tot": {"hyper": 0, "power": 1},
                        "cost_tot": {"hyper": 0, "power": 1},
                        "emis_tot": {"hyper": 0, "power": 1},
                        "power_pen":{"hyper": 0, "power":1}}
                                         ) 
 ```
