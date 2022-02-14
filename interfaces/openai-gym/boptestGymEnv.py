import gym
import requests
import numpy as np
import inspect
import json,collections
import os
import custom_kpi_calculator as kpicalculation
import sys
from pathlib import Path
sys.path.append("../..")
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent / 'actb_client'))
from actb_client import ActbClient
from custom_kpi import custom_kpi_calculator as kpicalculation
import time as _time


from collections import OrderedDict
from pprint import pformat
from gym import spaces


class BoptestGymEnv(gym.Env):
    '''
    BOPTEST Environment that follows gym interface.
    This environment allows the interaction of RL agents with building
    emulator models from BOPTEST. 
     
    '''
    
    metadata = {'render.modes': ['console']}

    def __init__(self, 
                 url                = 'http://127.0.0.1:80',
                 testcase           = None,
                 actions            = ['oveDSet_activate'],
                 building_obs       = ['senTRoom_y'],
                 forecast_obs       = {'TDryBul': [0, 4], 'winDir': [0], 'HGloHor': [0, 1]},
                 lower_obs_bounds   = None,
                 upper_obs_bounds   = None,
                 reward             = ['reward'],
                 episode_length     = 3*3600,
                 n_obs              = False,
                 random_start_time  = False,
                 excluding_periods  = None,
                 forecasting_period = None,
                 DR_event           = False,
                 DR_time            = [3600 * 14, 3600 * 16],
                 dr_power_limit     = 10000,
                 start_time         = 0,
                 warmup_period      = 0,
                 Ts                 = 900,
                 occupancy_sch      = [6,20],
                 dr_obs             = [0, 1],
                 dr_opt             = 2,
                 kpi_zones          = ['0','1','2','3','4'],
                 KPI_rewards        = {"ener_tot": {"hyper": -1, "power": 1},
                                       "tdis_tot": {"hyper": 0, "power": 1},
                                       "idis_tot": {"hyper": 0, "power": 1},
                                       "cost_tot": {"hyper": 0, "power": 1},
                                       "emis_tot": {"hyper": 0, "power": 1}}):



        super(BoptestGymEnv,self).__init__()
        
        self.url                    = url
        self.actions                = actions        
        self.building_obs           = building_obs
        self.forecast_obs           = forecast_obs
        self.lower_obs_bounds       = lower_obs_bounds
        self.upper_obs_bounds       = upper_obs_bounds
        self.episode_length         = episode_length
        self.random_start_time      = random_start_time
        self.excluding_periods      = excluding_periods
        self.start_time             = start_time
        self.warmup_period          = warmup_period
        self.reward                 = reward
        self.forecasting_period     = forecasting_period
        self.KPI_rewards            = KPI_rewards
        self.kpi_zones              = kpi_zones
        self.n_obs                  = n_obs
        self.DR_event               = DR_event
        self.DR_time                = DR_time
        self.Ts                     = Ts
        self.occupancy_sch          = occupancy_sch
        self.kpi_timestep           = {key: 0 for key in ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']}
        self.kpi_integral_last_step = {key: 0 for key in ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']}
        self.building_y             = []
        self.info                   = {}
        self.dr_obs                 = dr_obs
        self.u                      = None
        self.dr_opt                 = dr_opt
        self.dr_power_limit         = dr_power_limit
        self.testcase = testcase
        self.initparams = {'start_time': self.start_time,
                                 'warmup_period': self.warmup_period}
        self.client = ActbClient(url)
        self.client.stop_all()
        self.client.select(self.testcase)
        
        # Avoid surpassing the end of the year during an episode
        self.end_year_margin = self.episode_length


        
        #=============================================================
        # Get test information
        #=============================================================
        # Test case name
        self.name = self.client.name()
        print('Name:\t\t\t\t{0}'.format(self.name))
        print("\n")

        # Measurements available
        self.all_measurement_vars = self.client.measurements()
        print('Measurements:\t\t\t{0}'.format(self.all_measurement_vars))
        print("\n")

        # Inputs available
        self.all_input_vars = self.client.inputs()
        print('Control Inputs:\t\t\t{0}'.format(self.all_input_vars))
        print("\n")

        # Default simulation step
        self.step_def = self.client.get_step()
        print('Default Simulation Step:\t{0}'.format(self.step_def))
        print("\n")

        # Default forecast parameters
        self.forecast_def = self.client.get_forecast_parameters()
        print('Default Forecast Interval:\t{0} '.format(self.forecast_def['interval']))
        print('Default Forecast Horizon:\t{0} '.format(self.forecast_def['horizon']))
        print("\n")
        
        # Define gym observation space
        self.observation_space = spaces.Box(low  = np.array(self.lower_obs_bounds), 
                                            high = np.array(self.upper_obs_bounds), 
                                            dtype= np.float32)    
        
        #=============================================================
        # Define action space
        #=============================================================
        # Assert that actions belong to the inputs in the emulator model
        for act in self.actions:
            if not (act in self.all_input_vars.keys()):
                raise ReferenceError(\
                 '"{0}" does not belong to the set of inputs to this '\
                 'emulator model. \n'\
                 'Set of inputs: \n{1}\n'.format(act, list(self.all_input_vars.keys()) ))

        # Parse minimum and maximum values for actions
        self.lower_act_bounds = []
        self.upper_act_bounds = []
        for act in self.actions:
            self.lower_act_bounds.append(self.all_input_vars[act]['Minimum'])
            self.upper_act_bounds.append(self.all_input_vars[act]['Maximum'])
        
        # Define gym action space
        self.action_space = spaces.Box(low  = np.array(self.lower_act_bounds), 
                                       high = np.array(self.upper_act_bounds), 
                                       dtype= np.float32)
        self.client.stop_all()


    def __str__(self):
        '''
        Print a summary of the environment. 
        
        '''
        
        # Get a summary of the environment
        summary = self.get_summary()
        
        # Create a printable string from summary
        s = '\n'
        
        # Iterate over summary, which has two layers of key,value pairs
        for k1,v1 in summary.items():
            s += '='*len(k1) + '\n'
            s += k1 + '\n'
            s += '='*len(k1) + '\n\n'
            for k2,v2 in v1.items():
                s += k2 + '\n'
                s += '-'*len(k2) + '\n'
                s += v2 + '\n\n'

        return s
    
    def get_summary(self):
        '''
        Get a summary of the environment.
        
        Returns
        -------
        summary: OrderedDict
            A dictionary mapping keys and values that fully describe the 
            environment. 
        
        '''
        
        summary = OrderedDict()
        
        summary['BOPTEST CASE INFORMATION'] = OrderedDict()
        summary['BOPTEST CASE INFORMATION']['Test case name'] = pformat(self.name)
        summary['BOPTEST CASE INFORMATION']['All measurement variables'] = pformat(self.all_measurement_vars)
        summary['BOPTEST CASE INFORMATION']['All forecasting variables'] = pformat(list(self.all_forecasting_vars.keys()))
        summary['BOPTEST CASE INFORMATION']['All input variables'] = pformat(self.all_input_vars)
        summary['BOPTEST CASE INFORMATION']['Default simulation step (seconds)'] = pformat(self.step_def)
        summary['BOPTEST CASE INFORMATION']['Default forecasting parameters (seconds)'] = pformat(self.forecast_def)
        
        
        summary['GYM ENVIRONMENT INFORMATION'] = OrderedDict()
        summary['GYM ENVIRONMENT INFORMATION']['Observation space'] = pformat(self.observation_space)
        summary['GYM ENVIRONMENT INFORMATION']['Action space'] = pformat(self.action_space)
        summary['GYM ENVIRONMENT INFORMATION']['Is a predictive environment'] = pformat(self.is_predictive)
        summary['GYM ENVIRONMENT INFORMATION']['Forecasting period (seconds)'] = pformat(self.forecasting_period)
        summary['GYM ENVIRONMENT INFORMATION']['Measurement variables used in observation space'] = pformat(self.measurement_vars)
        summary['GYM ENVIRONMENT INFORMATION']['Forecasting variables used in observation space'] = pformat(self.forecasting_vars)
        summary['GYM ENVIRONMENT INFORMATION']['Sampling time (seconds)'] = pformat(self.Ts)
        summary['GYM ENVIRONMENT INFORMATION']['Random start time'] = pformat(self.random_start_time)
        summary['GYM ENVIRONMENT INFORMATION']['Excluding periods (seconds from the beginning of the year)'] = pformat(self.excluding_periods)
        summary['GYM ENVIRONMENT INFORMATION']['Warmup period for each episode (seconds)'] = pformat(self.warmup_period)
        summary['GYM ENVIRONMENT INFORMATION']['Maximum episode length (seconds)'] = pformat(self.episode_length)
        summary['GYM ENVIRONMENT INFORMATION']['Environment reward function (source code)'] = pformat(inspect.getsource(self.compute_reward))
        summary['GYM ENVIRONMENT INFORMATION']['Environment hierarchy'] = pformat(inspect.getmro(self.__class__))
        
        return summary

    def save_summary(self, file_name='summary'):
        '''
        Saves the environment summary in a `.json` file. 
        
        Parameters
        ----------
        file_name: string
            File name where the summary will be saved in `.json` format
        
        '''
        
        summary = self.get_summary()
        with open('{}.json'.format(file_name), 'w') as outfile:  
            json.dump(summary, outfile) 
            
  

    def reset(self):            

        # sudoPassword = self.password
        #
        # print("TESTING: Stopping Docker container")
        # cur_path = str(Path(__file__).parent.absolute())
        # command = 'bash '+cur_path+'/stop.sh'
        # p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))
        # _time.sleep(3)
        #
        # print("TESTING: Starting Docker container")
        # command = 'bash '+cur_path+'/start.sh'
        # p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))
        # _time.sleep(10)

        # Initialize the building simulation
        params = {'start_time': self.start_time,
                                 'warmup_period': self.warmup_period}
        self.client.set_step(self.Ts)
        res = self.client.reset(**params)

        if res:
            print('Successfully initialized the simulation')

        # Set simulation step
        print('Setting simulation step to {0}.'.format(self.Ts))

        # Get forecast values
        forecasts = self.client.get_forecasts()

        self.forecast_y = forecasts

        # Initialize objective integrand
        self.kpi_timestep = {key: 0 for key in ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']}
        self.kpi_integral_last_step = {key: 0 for key in ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']}

        self.building_y = res

        # Get measurements at the end of the initialization period
        meas = self.get_measurements(res, forecasts)
        
        return meas


    def step(self, action):              
        # Initialize inputs to send through BOPTEST Rest API
        u = {}
        # u = { #Low-level heating coil
        #      'PSZACcontroller_oveHeaCor_u': 0,
        #      'PSZACcontroller_oveHeaCor_activate': 0,
        #      'PSZACcontroller_oveHeaPer1_u': 0,
        #      'PSZACcontroller_oveHeaPer1_activate': 0,
        #      'PSZACcontroller_oveHeaPer2_u': 0,
        #      'PSZACcontroller_oveHeaPer2_activate': 0,
        #      'PSZACcontroller_oveHeaPer3_u': 0,
        #      'PSZACcontroller_oveHeaPer3_activate': 0,
        #      'PSZACcontroller_oveHeaPer4_u': 0,
        #      'PSZACcontroller_oveHeaPer4_activate': 0,
        #     # Heating Setpoint Control
        #      'PSZACcontroller_oveHeaStpCor_u': 0,
        #      'PSZACcontroller_oveHeaStpCor_activate': 0,
        #      'PSZACcontroller_oveHeaStpPer1_u': 0,
        #      'PSZACcontroller_oveHeaStpPer1_activate': 0,
        #      'PSZACcontroller_oveHeaStpPer2_u': 0,
        #      'PSZACcontroller_oveHeaStpPer2_activate': 0,
        #      'PSZACcontroller_oveHeaStpPer3_u': 0,
        #      'PSZACcontroller_oveHeaStpPer3_activate': 0,
        #      'PSZACcontroller_oveHeaStpPer4_u': 0,
        #      'PSZACcontroller_oveHeaStpPer4_activate': 0,
        #     # Low-level damper control
        #      'PSZACcontroller_oveDamCor_u': 0,   # 0 to 0.5 m3/s
        #      'PSZACcontroller_oveDamCor_activate': 0,
        #      'PSZACcontroller_oveDamP1_u': 0,
        #      'PSZACcontroller_oveDamP1_activate': 0,
        #      'PSZACcontroller_oveDamP2_u': 0,
        #      'PSZACcontroller_oveDamP2_activate': 0,
        #      'PSZACcontroller_oveDamP3_u': 0,
        #      'PSZACcontroller_oveDamP3_activate': 0,
        #      'PSZACcontroller_oveDamP4_u': 0,
        #      'PSZACcontroller_oveDamP4_activate': 0,
        #      # Cooling setpoint Control
        #      'PSZACcontroller_oveCooStpCor_u': 0,
        #      'PSZACcontroller_oveCooStpCor_activate': 0,
        #      'PSZACcontroller_oveCooStpPer1_u': 0,
        #      'PSZACcontroller_oveCooStpPer1_activate': 0,
        #      'PSZACcontroller_oveCooStpPer4_u': 0,
        #      'PSZACcontroller_oveCooStpPer4_activate': 0,
        #      'PSZACcontroller_oveCooStpPer3_u': 0,
        #      'PSZACcontroller_oveCooStpPer3_activate': 0,
        #      'PSZACcontroller_oveCooStpPer2_u': 0,
        #      'PSZACcontroller_oveCooStpPer2_activate': 0,
        #      # Low-level cooling coil control
        #      'PSZACcontroller_oveCooCor_u': 0,
        #      'PSZACcontroller_oveCooCor_activate': 0,
        #      'PSZACcontroller_oveCooPer1_u': 0,
        #      'PSZACcontroller_oveCooPer1_activate': 0,
        #      'PSZACcontroller_oveCooPer2_u': 0,
        #      'PSZACcontroller_oveCooPer2_activate': 0,
        #      'PSZACcontroller_oveCooPer3_u': 0,
        #      'PSZACcontroller_oveCooPer3_activate': 0,
        #      'PSZACcontroller_oveCooPer4_u': 0,
        #      'PSZACcontroller_oveCooPer4_activate': 0
        #       }

        # Assign values to inputs if any
        for i, act in enumerate(self.actions):
            # Assign value
            u[act] = action[i]
            
            # Indicate that the input is active
            u[act.replace('_u','_activate')] = 1.
                
        # Advance a BOPTEST simulation
        res = self.client.advance(control_u = u)
        self.building_y = res

        # Get forecast values
        forecasts = self.client.get_forecasts()
        self.forecast_y = forecasts
        self.u = u
        
        # Compute reward of this (state-action-state') tuple
        reward = self.compute_reward()
        
        # Define whether we've finished the episode
        done = res['time'] >= self.start_time + self.episode_length
        
        # Optionally we can pass additional info - here individual zone rewards are returned
        info = self.get_info()

        # Get measurements at the end of this time step
        meas = self.get_measurements(res, forecasts)
                
        return meas, reward, done, info

    def get_info(self):
        return self.info


    def normalize_obs(self,obs):
        if self.DR_event == True:
            low = self.observation_space.low[0:-len(self.dr_obs)]
            high = self.observation_space.high[0:-len(self.dr_obs)]
        else:
            low = self.observation_space.low
            high = self.observation_space.high

        norm_obs= (obs-low)/(high-low)
        norm_obs = norm_obs.tolist()

        return norm_obs

    def set_DR_time(self, DR_time):
        self.DR_time = DR_time

    def get_DR_signal(self):
        hour_dec = self.building_y['senHouDec_y']
        DR_signal = list()
        start_DR = self.DR_time[0] / 3600
        end_DR = self.DR_time[1] / 3600


        if self.dr_opt == 2:
            count = 0
            for hr in self.dr_obs:
                obs_hour = hour_dec + hr
                count += 1
                if count == 1:
                    if (obs_hour >= start_DR) and (obs_hour < end_DR):
                        dr_signal = 1
                    else:
                        dr_signal = 0
                else:
                    if (obs_hour >= start_DR):
                        dr_signal = 1
                    else:
                        dr_signal = 0
                DR_signal.append(dr_signal)
        else:
            for hr in self.dr_obs:
                obs_hour = hour_dec + hr
                if (obs_hour >= start_DR) and (obs_hour < end_DR):
                    dr_signal = 1
                else:
                    dr_signal = 0
                DR_signal.append(dr_signal)

        if self.dr_opt == 2:
            if DR_signal[0] == 1:
                for i in range(len(DR_signal)):
                    if (i + 1) < len(DR_signal):
                        DR_signal[i + 1] = 0

            if hour_dec > end_DR:
                DR_signal = list()
                #print("check condition")
                for i in range(len(self.dr_obs)):
                    #print("Check {}".format(i))
                    dr_signal = 0
                    DR_signal.append(dr_signal)

        # print (DR_signal)
        return DR_signal


    def get_input_hist(self):
        return self.u

    def get_weather_forecast(self,current=True):
        return (self.forecast_y)

    def get_measurements(self, res, forecasts):

        # Get reults at the end of the simulation step
        observations = []

        for building_obs in self.building_obs:
            observations.append(res[building_obs])

        for forecast_obs in self.forecast_obs:
            for horizon in self.forecast_obs[forecast_obs]:
                if (forecast_obs == 'TDryBul') or (forecast_obs== 'TDewPoi')or (forecast_obs == 'TWetBul'):
                    observations.append(forecasts[forecast_obs][horizon] + 0)
                else:
                    observations.append(forecasts[forecast_obs][horizon])

        if self.n_obs == True:
            observations = self.normalize_obs(observations)

        if self.DR_event == True:
            DR_signal = self.get_DR_signal()
            for obs in DR_signal:
                observations.append(obs)



        # Reformat observations
        meas = np.array(observations).astype(np.float32)
        return meas
    
  

    def close(self):
        pass
    
    def compute_reward(self):

        # Compute BOPTEST core kpis
        kpis = self.client.kpis()
        kpis_keys = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']
        dr_kpis_keys = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot', 'power_pen']

        'spawnrefsmalloffice'

        reward = 0
        kpi_dict = {'spawnrefsmalloffice':  'custom_kpis_example_gym_spawnrefsmalloffice.config',
                    'spawnrefmediumoffice': 'custom_kpis_example_gym_spawnrefmediumoffice.config'}



        customized_kpi_config = str(Path(__file__).parent.absolute() / 'custom_kpi' / kpi_dict[self.testcase])
        # Define customized KPI if any
        customizedkpis = []  # Initialize customzied kpi calculation list
        customizedkpis_result = {}  # Initialize tracking of customized kpi calculation results
        if customized_kpi_config is not None:
            with open(customized_kpi_config) as f:
                config = json.load(f, object_pairs_hook=collections.OrderedDict)
            for key in config.keys():
                customizedkpis.append(kpicalculation.cutomizedKPI(config[key]))
                customizedkpis_result[kpicalculation.cutomizedKPI(config[key]).name] = []

        # Customized KPIs
        for customizedkpi in customizedkpis:
            customizedkpi.processing_data(self.building_y)  # Process data as needed for custom KPI
            customizedkpi_value = customizedkpi.calculation()  # Calculate custom KPI value
            customizedkpis_result[customizedkpi.name].append(round(customizedkpi_value, 2))  # Track custom KPI value
            # print('KPI:\t{0}:\t{1}'.format(customizedkpi.name, round(customizedkpi_value, 2)))  # Print custom KPI value
            kpi_dict[str(customizedkpi.name)] = round(customizedkpi_value, 2)

        hour = self.building_y['senHouDec_y']

        if (hour >= 6) & (hour < 22):
            upp_setpoint = 297.15
            low_setpoint = 294.15
        else:
            upp_setpoint = 303.15
            low_setpoint = 288.15

        Temp_keys = [x for x in kpi_dict.keys() if "Temp" in x]
        Power_keys = [x for x in kpi_dict.keys() if "power" in x]
        power_dict = {x: kpi_dict[x] for x in Power_keys}
        energy_dict = {}

        print (power_dict)

        power_dict['average_power_tot'] = sum(power_dict.values())

        for key in Power_keys:
            energy_dict[key] = power_dict[key] * self.Ts / (3600 * 1000)  # change to energy

        for i in Temp_keys:
            if (kpi_dict[i] <= upp_setpoint) & (kpi_dict[i] >= low_setpoint):
                kpi_dict[i + '_Dev'] = 0
            elif (kpi_dict[i] >= upp_setpoint):
                kpi_dict[i + '_Dev'] = (kpi_dict[i] - upp_setpoint)
            else:
                kpi_dict[i + '_Dev'] = low_setpoint - kpi_dict[i]

        Temp_dev_keys = [x for x in kpi_dict.keys() if "Dev" in x]
        kpi_tdis = {x: kpi_dict[x] for x in Temp_dev_keys}

        sel_kpi_tdis_keys = ["Temp_" + x + "_Dev" for x in self.kpi_zones]
        sel_kpi_ener_keys = ["Average_power_" + x for x in self.kpi_zones]
        sel_kpi_tdis = {x: kpi_tdis[x] for x in sel_kpi_tdis_keys}
        sel_kpi_ener = {x: energy_dict[x] for x in sel_kpi_ener_keys}


        print ("Debugging")
        print ("KPI_Thermal_Discount : {}".format(kpi_tdis))
        print ("Sel_kpi_tdis: {}".format(sel_kpi_tdis))
        print ("energy_dict : {}".format(energy_dict))
        print ("sel_kpi_ener : {}".format(sel_kpi_ener))
        print("power_dict : {}".format(power_dict))


        R = []
        R.append(self.KPI_rewards['tdis_tot']["hyper"] * kpi_tdis['Temp_0_Dev'] + self.KPI_rewards['ener_tot']["hyper"] * energy_dict['Average_power_0'])
        R.append(self.KPI_rewards['tdis_tot']["hyper"] * kpi_tdis['Temp_1_Dev'] + self.KPI_rewards['ener_tot']["hyper"] * energy_dict['Average_power_1'])
        R.append(self.KPI_rewards['tdis_tot']["hyper"] * kpi_tdis['Temp_2_Dev'] + self.KPI_rewards['ener_tot']["hyper"] * energy_dict['Average_power_2'])
        R.append(self.KPI_rewards['tdis_tot']["hyper"] * kpi_tdis['Temp_3_Dev'] + self.KPI_rewards['ener_tot']["hyper"] * energy_dict['Average_power_3'])
        R.append(self.KPI_rewards['tdis_tot']["hyper"] * kpi_tdis['Temp_4_Dev'] + self.KPI_rewards['ener_tot']["hyper"] * energy_dict['Average_power_4'])

        power_dict['power_pen'] = max(0,power_dict['average_power_tot'] - self.dr_power_limit)
        self.info['rewards_pow_pen'] = self.KPI_rewards['power_pen']["hyper"]* power_dict['power_pen']


        self.info['rewards_zone_0'] = R[0]
        self.info['rewards_zone_1'] = R[1]
        self.info['rewards_zone_2'] = R[2]
        self.info['rewards_zone_3'] = R[3]
        self.info['rewards_zone_4'] = R[4]

        for kpi_name in kpis_keys:
            self.kpi_timestep[kpi_name] = kpis[kpi_name] - self.kpi_integral_last_step[kpi_name]
            self.kpi_integral_last_step[kpi_name] = kpis[kpi_name]

        # change to zone no
        if len(self.kpi_zones) <= 5:
            self.kpi_timestep['ener_tot'] = sum(sel_kpi_ener.values())
            self.kpi_timestep['tdis_tot'] = sum(sel_kpi_tdis.values())


        # Compute rewards
        for kpi in kpis_keys:
            reward = reward + self.KPI_rewards[kpi]["hyper"]*self.kpi_timestep[kpi]**(self.KPI_rewards[kpi]["power"])

        self.individual_rewards = {"Energy": self.kpi_timestep['ener_tot'],
                                   "Thermal_Discomfort": self.kpi_timestep['tdis_tot'],
                                   "Power_Penalty": self.info['rewards_pow_pen']}

        if self.DR_event == True :
            reward = reward + self.info['rewards_pow_pen']

        return reward

    def compute_done(self, res, reward=None):
        done = res['time'] >= self.start_time + self.episode_length
        return done

    def get_observations(self, res):
        # Initialize observations
        observations = []

        # Get measurements at the end of the simulation step
        for obs in self.measurement_vars:
            observations.append(res[obs])
        
        # Get predictions if this is a predictive agent
        if self.is_predictive:
            forecast = self.client.get_forecasts()
            for var in self.forecasting_vars:
                for i in range(self.fore_n):
                    observations.append(forecast[var][i])
            
        # Reformat observations
        observations = np.array(observations).astype(np.float32)
        return observations
    
    def get_KPIs(self):
        return self.client.kpis()

    def change_rewards_weights(self,KPI_rewards):
        self.KPI_rewards = KPI_rewards

    def change_dr_limit(self,dr_power_limit):
        self.dr_power_limit = dr_power_limit

    def get_individual_rewards(self):
        return self.individual_rewards

    def get_building_states(self):
        return (self.building_y)

    def print_KPIs(self):
        kpi = self.get_KPIs()
        for key in kpi.keys():
            if key == 'ener_tot':
                unit = 'kWh'
            elif key == 'tdis_tot':
                unit = 'Kh'
            elif key == 'idis_tot':
                unit = 'ppmh'
            elif key == 'cost_tot':
                unit = 'Euro or $'
            elif key == 'emis_tot':
                unit = 'KgCO2'
            else:
                unit = None
            print('{0}: {1} {2}'.format(key, kpi[key], unit))

    def save_current(self):



    def save_episode(self,path):
        return


if __name__ == "__main__":
    # Instantiate the env    
    env = BoptestGymEnv()
    obs = env.reset(env.testcase, **env.initparams)
    print (env.get_summary())
    print('Observation space: {}'.format(env.observation_space))
    print('Action space: {}'.format(env.action_space))
    