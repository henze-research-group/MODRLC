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
