'''
Created on Jun 4, 2020

@author: Javier Arroyo & Sourav Dey

'''

import random
import gym
import copy
import requests
import numpy as np
import pandas as pd
import inspect
import json,collections
import os
import custom_kpi_calculator as kpicalculation
import sys
sys.path.append("../..")
from examples.python.custom_kpi import custom_kpi_calculator as kpicalculation
import time as _time

from collections import OrderedDict
from pprint import pformat
from gym import spaces
#from stable_baselines.common.env_checker import check_env
#from stable_baselines.results_plotter import load_results, ts2xy
#from stable_baselines.common.callbacks import BaseCallback


class BoptestGymEnv(gym.Env):
    '''
    BOPTEST Environment that follows gym interface.
    This environment allows the interaction of RL agents with building
    emulator models from BOPTEST. 
     
    '''
    
    metadata = {'render.modes': ['console']}

    def __init__(self, 
                 url                = 'http://127.0.0.1:5000',
                 password           = None
                 actions            = ['oveDSet_activate'],
                 building_obs       = ['senTRoom_y'],
                 forecast_obs       = {'TDryBul': [0, 4], 'winDir': [0], 'HGloHor': [0, 1]},
                 observations       = {'senTRoom_y':(280.,310.)},
                 lower_obs_bounds   = None,
                 upper_obs_bounds   = None,
                 reward             = ['reward'],
                 max_episode_length = 3*3600,
                 n_obs              =True,
                 random_start_time  = False,
                 excluding_periods  = None,
                 forecasting_period = None,
                 DR_event           = False,
                 DR_time            =[3600 * 14, 3600 * 16],
                 start_time         = 0,
                 warmup_period      = 0,
                 Ts                 = 900,
                 occupancy_sch      = [8,18],
                 dr_obs             = [0, 1],
                 kpi_zones          = ['0','1','2','3','4'],
                 KPI_rewards        = {"ener_tot": {"hyper": -1, "power": 1},
                                       "tdis_tot": {"hyper": 0, "power": 1},
                                       "idis_tot": {"hyper": 0, "power": 1},
                                       "cost_tot": {"hyper": 0, "power": 1},
                                       "emis_tot": {"hyper": 0, "power": 1}}):


        '''
        Parameters
        ----------
        url: string
            Rest API url for communication with the BOPTEST interface
        actions: list
            List of strings indicating the action space. The bounds of 
            each variable from the action space the are retrieved from 
            the overwrite block attributes of the BOPTEST test case
        observations: dictionary
            Dictionary mapping observation keys to a tuple with the lower
            and upper bound of each observation. Observation keys must 
            belong either to the set of measurements or to the set of 
            forecasting variables of the BOPTEST test case. Contrary to 
            the actions, the expected minimum and maximum values of the 
            measurement and forecasting variables are not provided from 
            the BOPTEST framework, although they are still relevant here 
            e.g. for normalization or discretization. Therefore, these 
            bounds need to be provided by the user. 
        reward: list
            List with string indicating the reward column name in a replay
            buffer of data in case the algorithm is going to use pretraining
        max_episode_length: integer
            Maximum duration of each episode in seconds
        random_start_time: boolean
            Set to True if desired to use a random start time for each episode
        excluding_periods: list of tuples
            List where each element is a tuple indicating the start and 
            end time of the periods that should not overlap with any 
            episode used for training. Example:
            excluding_periods = [(31*24*3600,  31*24*3600+14*24*3600),
                                (304*24*3600, 304*24*3600+14*24*3600)]
            This is only used when `random_start_time=True`
        forecasting_period: integer, default is None
            Number of seconds for the forecasting horizon. The observations
            will be extended for each of the forecasting variables indicated
            in the `observations` dictionary argument. Specifically, a number
            of `int(self.forecasting_period/self.Ts)` observations per 
            forecasting variable will be included in the observation space.
            Each of these observations correspond to the foresighted 
            variable `i` steps ahead from the actual observation time. 
            Note that it's allowed to use `forecasting_period=0` when the
            intention is to retrieve boundary condition data at the actual
            observation time, useful e.g. for temperature setpoints or 
            ambient temperature. 
        start_time: integer
            Initial fixed episode time in seconds from beginning of the 
            year for each episode. Use in combination with 
            `random_start_time=False` 
        warmup_period: integer
            Desired simulation period to initialize each episode 
        Ts: integer
            Sampling time in seconds
            
        '''
        
        super(BoptestGymEnv,self).__init__()
        
        self.url                    = url
        self.actions                = actions
        self.observations           = list(observations.keys())
        self.building_obs           = building_obs
        self.forecast_obs           = forecast_obs
        self.lower_obs_bounds       = lower_obs_bounds
        self.upper_obs_bounds       = upper_obs_bounds
        self.max_episode_length     = max_episode_length
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
        self.password               = password




        
        # Avoid surpassing the end of the year during an episode
        self.end_year_margin = self.max_episode_length
        
        #=============================================================
        # Get test information
        #=============================================================
        # Test case name
        self.name = requests.get('{0}/name'.format(url)).json()
        print('Name:\t\t\t\t{0}'.format(self.name))
        print("\n")

        # Measurements available
        self.all_measurement_vars = requests.get('{0}/measurements'.format(url)).json()
        print('Measurements:\t\t\t{0}'.format(self.all_measurement_vars))
        print("\n")

        # Forecasting variables available
        self.all_forecasting_vars = requests.get('{0}/forecast'.format(url)).json()
        print('Forecasting variables:\t\t\t{0}'.format(self.all_forecasting_vars))
        print("\n")


        # Inputs available
        self.all_input_vars = requests.get('{0}/inputs'.format(url)).json()
        print('Control Inputs:\t\t\t{0}'.format(self.all_input_vars))
        print("\n")

        # Default simulation step
        self.step_def = requests.get('{0}/step'.format(url)).json()
        print('Default Simulation Step:\t{0}'.format(self.step_def))
        print("\n")

        # Default forecast parameters
        self.forecast_def = requests.get('{0}/forecast_parameters'.format(url)).json()
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
        #summary['BOPTEST CASE INFORMATION']['Default scenario'] = pformat(self.scenario_def)    # edit 01
        
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
        summary['GYM ENVIRONMENT INFORMATION']['Maximum episode length (seconds)'] = pformat(self.max_episode_length)
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
            
    def load_summary(self, file_name='summary'):
        '''
        Loads an environment summary from a `.json` file. 
        
        Parameters
        ----------
        file_name: string
            File in `.json` format from where the summary is to be loaded
        
        Returns
        -------
        summary: OrderedDict
            A summary of an environment
            
        '''
        
        with open(file_name+'.json', 'r') as f:
            summary = json.load(f, object_pairs_hook=OrderedDict)
        
        return summary

    def reset(self):
        '''

        Returns
        -------
        observations: numpy array
            Reformatted observations that include measurements and 
            predictions (if any) at the end of the initialization. 
         
        '''        
        
        def find_start_time():
            '''Recursive method to find a random start time out of 
            `excluding_periods`. An episode and an excluding_period that
            are just touching each other are not considered as being 
            overlapped. 
            
            '''
            start_time = random.randint(0, 3.1536e+7-self.end_year_margin)
            episode = (start_time, start_time+self.max_episode_length)
            if self.excluding_periods is not None:
                for period in self.excluding_periods:
                    if episode[0] < period[1] and period[0] < episode[1]:
                        # There is overlapping between episode and this period
                        # Try to find a good starting time again
                        start_time = find_start_time()
            # This point is reached only when a good starting point is found
            return start_time
        
        # Assign random start_time if it is None
        if self.random_start_time:
            self.start_time = find_start_time()

        sudoPassword = self.password

        print("TESTING: Stopping Docker container")
        command = 'bash stop.sh'
        p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))
        _time.sleep(3)

        print("TESTING: Starting Docker container")
        command = 'bash start.sh'
        p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))
        _time.sleep(10)

        # Initialize the building simulation
        res = requests.put('{0}/initialize'.format(self.url),
                           data={'start_time': self.start_time,
                                 'warmup_period': self.warmup_period}).json()

        if res:
            print('Successfully initialized the simulation')

        # Set simulation step
        requests.put('{0}/step'.format(self.url), data={'step': self.Ts})

        print('Setting simulation step to {0}.'.format(self.Ts))

        # Get forecast values
        forecasts = requests.get('{0}/forecast'.format(self.url)).json()

        self.forecast_y = forecasts

        # Set forecasting parameters if predictive
        # if self.is_predictive:
        #     forecast_parameters = {'horizon':self.forecasting_period, 'interval':self.Ts}
        #     requests.put('{0}/forecast_parameters'.format(self.url),
        #                  data=forecast_parameters)

        # Initialize objective integrand
        self.kpi_timestep = {key: 0 for key in ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']}
        self.kpi_integral_last_step = {key: 0 for key in ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']}

        self.building_y = res

        # Get measurements at the end of the initialization period
        meas = self.get_measurements(res, forecasts)
        
        return meas


    def step(self, action):
        '''
        Advance the simulation one time step
        
        Parameters
        ----------
        action: list
            List of actions computed by the agent to be implemented 
            in this step
            
        Returns
        -------
        observations: numpy array
            Observations at the end of this time step
        reward: float
            Reward for the state-action pair implemented
        done: boolean
            True if episode is finished after this step
        info: dictionary
            Additional information for this step
        
        '''
        # Initialize inputs to send through BOPTEST Rest API
        u = { #Low-level heating coil
             'PSZACcontroller_oveHeaCor_u': 0,
             'PSZACcontroller_oveHeaCor_activate': 0,
             'PSZACcontroller_oveHeaPer1_u': 0,
             'PSZACcontroller_oveHeaPer1_activate': 0,
             'PSZACcontroller_oveHeaPer2_u': 0,
             'PSZACcontroller_oveHeaPer2_activate': 0,
             'PSZACcontroller_oveHeaPer3_u': 0,
             'PSZACcontroller_oveHeaPer3_activate': 0,
             'PSZACcontroller_oveHeaPer4_u': 0,
             'PSZACcontroller_oveHeaPer4_activate': 0,
            # Heating Setpoint Control
             'PSZACcontroller_oveHeaStpCor_u': 0,
             'PSZACcontroller_oveHeaStpCor_activate': 0,
             'PSZACcontroller_oveHeaStpPer1_u': 0,
             'PSZACcontroller_oveHeaStpPer1_activate': 0,
             'PSZACcontroller_oveHeaStpPer2_u': 0,
             'PSZACcontroller_oveHeaStpPer2_activate': 0,
             'PSZACcontroller_oveHeaStpPer3_u': 0,
             'PSZACcontroller_oveHeaStpPer3_activate': 0,
             'PSZACcontroller_oveHeaStpPer4_u': 0,
             'PSZACcontroller_oveHeaStpPer4_activate': 0,
            # Low-level damper control
             'PSZACcontroller_oveDamCor_u': 0,   # 0 to 0.5 m3/s
             'PSZACcontroller_oveDamCor_activate': 0,
             'PSZACcontroller_oveDamP1_u': 0,
             'PSZACcontroller_oveDamP1_activate': 0,
             'PSZACcontroller_oveDamP2_u': 0,
             'PSZACcontroller_oveDamP2_activate': 0,
             'PSZACcontroller_oveDamP3_u': 0,
             'PSZACcontroller_oveDamP3_activate': 0,
             'PSZACcontroller_oveDamP4_u': 0,
             'PSZACcontroller_oveDamP4_activate': 0,
             # Cooling setpoint Control
             'PSZACcontroller_oveCooStpCor_u': 0,
             'PSZACcontroller_oveCooStpCor_activate': 0,
             'PSZACcontroller_oveCooStpPer1_u': 0,
             'PSZACcontroller_oveCooStpPer1_activate': 0,
             'PSZACcontroller_oveCooStpPer4_u': 0,
             'PSZACcontroller_oveCooStpPer4_activate': 0,
             'PSZACcontroller_oveCooStpPer3_u': 0,
             'PSZACcontroller_oveCooStpPer3_activate': 0,
             'PSZACcontroller_oveCooStpPer2_u': 0,
             'PSZACcontroller_oveCooStpPer2_activate': 0,
             # Low-level cooling coil control
             'PSZACcontroller_oveCooCor_u': 0,
             'PSZACcontroller_oveCooCor_activate': 0,
             'PSZACcontroller_oveCooPer1_u': 0,
             'PSZACcontroller_oveCooPer1_activate': 0,
             'PSZACcontroller_oveCooPer2_u': 0,
             'PSZACcontroller_oveCooPer2_activate': 0,
             'PSZACcontroller_oveCooPer3_u': 0,
             'PSZACcontroller_oveCooPer3_activate': 0,
             'PSZACcontroller_oveCooPer4_u': 0,
             'PSZACcontroller_oveCooPer4_activate': 0
              }

        # Assign values to inputs if any
        for i, act in enumerate(self.actions):
            # Assign value
            u[act] = action[i]
            
            # Indicate that the input is active
            u[act.replace('_u','_activate')] = 1.
                
        # Advance a BOPTEST simulation
        res = requests.post('{0}/advance'.format(self.url), data=u).json()
        self.building_y = res

        # Get forecast values
        forecasts = requests.get('{0}/forecast'.format(self.url)).json()
        self.forecast_y = forecasts
        self.u = u
        
        # Compute reward of this (state-action-state') tuple
        reward = self.compute_reward()
        
        # Define whether we've finished the episode
        done = res['time'] >= self.start_time + self.max_episode_length
        
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

        opt = 2

        if opt == 2:
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

        if opt == 2:
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
                    observations.append(forecasts[forecast_obs][horizon] + 273.15)
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
    
    def render(self, mode='console'):
        '''
        Renders the process evolution 
        
        Parameters
        ----------
        mode: string
            Mode to be used for the renderization
        
        '''
        if mode != 'console':
            raise NotImplementedError()

    def close(self):
        pass
    
    def compute_reward(self):
        '''
        Compute the reward of last state-action-state' tuple. The 
        reward is implemented as the negated increase in the objective
        integrand function. In turn, this objective integrand function 
        is calculated as the sum of the total operational cost plus
        the weighted discomfort. 
        
        Returns
        -------
        Reward: float
            Reward of last state-action-state' tuple
        

        '''

        # Compute BOPTEST core kpis
        kpis = requests.get('{0}/kpi'.format(self.url)).json()

        kpis_keys = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']

        reward = 0

        kpi_dict = {}

        customized_kpi_config = 'custom_kpi/custom_kpis_example_gym.config'

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

        if (hour >= 8) & (hour < 18):
            upp_setpoint = 297.15
            low_setpoint = 294.15
        else:
            upp_setpoint = 300.15
            low_setpoint = 291.15

        Temp_keys = [x for x in kpi_dict.keys() if "Temp" in x]
        Power_keys = [x for x in kpi_dict.keys() if "power" in x]
        power_dict = {x: kpi_dict[x] for x in Power_keys}

        for key in Power_keys:
            power_dict[key] = power_dict[key] * self.Ts / (3600 * 1000)  # change to energy

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
        sel_kpi_ener = {x: power_dict[x] for x in sel_kpi_ener_keys}

        # print ("Debugging")
        # print (sel_kpi_tdis)
        # print (sel_kpi_ener)

        R = []

        R.append(self.KPI_rewards['ener_tot']["hyper"] * sel_kpi_tdis['Temp_0_Dev'] + self.KPI_rewards['tdis_tot']["hyper"]*sel_kpi_ener['Average_power_0'])
        R.append(self.KPI_rewards['ener_tot']["hyper"] * sel_kpi_tdis['Temp_1_Dev'] + self.KPI_rewards['tdis_tot']["hyper"] * sel_kpi_ener['Average_power_1'])
        R.append(self.KPI_rewards['ener_tot']["hyper"] * sel_kpi_tdis['Temp_2_Dev'] + self.KPI_rewards['tdis_tot']["hyper"] * sel_kpi_ener['Average_power_2'])
        R.append(self.KPI_rewards['ener_tot']["hyper"] * sel_kpi_tdis['Temp_3_Dev'] + self.KPI_rewards['tdis_tot']["hyper"] * sel_kpi_ener['Average_power_3'])
        R.append(self.KPI_rewards['ener_tot']["hyper"] * sel_kpi_tdis['Temp_4_Dev'] + self.KPI_rewards['tdis_tot']["hyper"] * sel_kpi_ener['Average_power_4'])

        self.info['rewards_0'] = R[0]
        self.info['rewards_1'] = R[1]
        self.info['rewards_2'] = R[2]
        self.info['rewards_3'] = R[3]
        self.info['rewards_4'] = R[4]

        for kpi_name in kpis_keys:
            self.kpi_timestep[kpi_name] = kpis[kpi_name] - self.kpi_integral_last_step[kpi_name]
            self.kpi_integral_last_step[kpi_name] = kpis[kpi_name]

        if len(self.kpi_zones) <= 5:
            self.kpi_timestep['ener_tot'] = sum(sel_kpi_ener.values())
            self.kpi_timestep['tdis_tot'] = sum(sel_kpi_tdis.values())


        # Compute rewards
        for kpi in kpis_keys:
            reward = reward + self.KPI_rewards[kpi]["hyper"]*self.kpi_timestep[kpi]**(self.KPI_rewards[kpi]["power"])

        return reward

    def compute_done(self, res, reward=None):
        done = res['time'] >= self.start_time + self.max_episode_length
        return done

    def get_observations(self, res):
        '''
        Get the observations, i.e. the conjunction of measurements and 
        forecasting variables if any. Also transforms the output to have
        the right format. 
        
        Parameters
        ----------
        res: dictionary
            Dictionary mapping simulation variables and their value at the
            end of the last time step. 
        
        Returns
        -------
        observations: numpy array
            Reformatted observations that include measurements and 
            predictions (if any) at the end of last step. 
        
        '''
        
        # Initialize observations
        observations = []

        # Get measurements at the end of the simulation step
        for obs in self.measurement_vars:
            observations.append(res[obs])
        
        # Get predictions if this is a predictive agent
        if self.is_predictive:
            forecast = requests.get('{0}/forecast'.format(self.url)).json()
            for var in self.forecasting_vars:
                for i in range(self.fore_n):
                    observations.append(forecast[var][i])
            
        # Reformat observations
        observations = np.array(observations).astype(np.float32)
                
        return observations
    
    def get_KPIs(self):
        '''Auxiliary method to get the so-colled core KPIs as computed in 
        the BOPTEST framework. This is handy when evaluating performance 
        of an agent in this environment. 
        
        '''
        
        # Compute BOPTEST core kpis
        kpis = requests.get('{0}/kpi'.format(self.url)).json()
        
        return kpis

    def change_rewards_weights(self,KPI_rewards):
        self.KPI_rewards = KPI_rewards

    def get_building_states(self):
        return (self.building_y)

    def print_KPIs(self):
        kpi = requests.get('{0}/kpi'.format(self.url)).json()
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


    def reformat_expert_traj(self, file_path='data.csv'):
        '''
        Reformats expert trajectory from a csv file to the npz format 
        required by Stable Baselines algorithms to be pre-trained.   
        
        Parameters
        ----------
        file_path: string
            path to csv file containing data
            
        Returns
        -------
        numpy_dict: numpy dictionary
            Numpy dictionary with the reformatted data
        
        Notes
        -----
        The resulting reformatted data considers only one episode from
        a long trajectory (a long time series). No recurrent policies 
        supported (mask and state not defined). 
        
        '''
        
        # We consider only one episode of index 0 that is never done
        n_episodes = 1
        ep_idx = 0
        done = False
        
        # Initialize data in the episode
        actions = []
        observations = []
        rewards = []
        episode_returns = np.zeros((n_episodes,))
        episode_starts = []
        
        # Initialize the only episode that we use
        episode_starts.append(True)
        reward_sum = 0.0

        df = pd.read_csv(file_path)
        for row in df.index:
            # Retrieve step information from csv
            obs     = df.loc[row, self.observations]
            action  = df.loc[row, self.actions]
            reward  = df.loc[row, self.reward]
            
            if obs.hasnans or action.hasnans or reward.hasnans:
                raise ValueError('Nans found in row {}'.format(row))
            
            # Append to data
            observations.append(np.array(obs))
            actions.append(np.array(action))
            rewards.append(np.array(reward))
            episode_starts.append(np.array(done))
            
            reward_sum += reward
        
        # This is hard coded as we only support one episode so far but
        # here we could implement some functionality for creating different 
        # episodes from csv data
        done = True
        if done:
            episode_returns[ep_idx] = reward_sum
            reward_sum = 0.0
    
        if isinstance(self.observation_space, spaces.Box):
            observations = np.concatenate(observations).reshape((-1,) + self.observation_space.shape)
        elif isinstance(self.observation_space, spaces.Discrete):
            observations = np.array(observations).reshape((-1, 1))
    
        if isinstance(self.action_space, spaces.Box):
            actions = np.concatenate(actions).reshape((-1,) + self.action_space.shape)
        elif isinstance(self.action_space, spaces.Discrete):
            actions = np.array(actions).reshape((-1, 1))
    
        rewards = np.array(rewards)
        episode_starts = np.array(episode_starts[:-1])
    
        assert len(observations) == len(actions)
    
        numpy_dict = {
            'actions': actions,
            'obs': observations,
            'rewards': rewards,
            'episode_returns': episode_returns,
            'episode_starts': episode_starts
        }  # type: Dict[str, np.ndarray]
    
        for key, val in numpy_dict.items():
            print(key, val.shape)
    
        np.savez(file_path.split('.')[-2], **numpy_dict)
        
        return numpy_dict


if __name__ == "__main__":
    
    # Instantiate the env    
    env = BoptestGymEnv()


    # Check the environment
    #check_env(env, warn=True)
    obs = env.reset()
    print (env.get_summary())
    env.render()
    print('Observation space: {}'.format(env.observation_space))
    print('Action space: {}'.format(env.action_space))
    