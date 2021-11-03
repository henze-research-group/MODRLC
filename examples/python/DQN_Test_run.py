
# GENERAL PACKAGE IMPORT
# ----------------------
import requests
import numpy as np;import pandas as pd
import json,collections
from DQN_Agent_test import DQN_Agent
from boptestGymEnv import BoptestGymEnv
import collections
from collections import OrderedDict
import math
import random


# ----------------------

# TEST CONTROLLER IMPORT
# ----------------------

# ----------------------

import time
# SETUP TEST CASE
# ---------------

start = time.time()

# GET TEST INFORMATION
# --------------------

step = 300
episode_length = 3600*24*1
start_time=24*3600*3 # Specify the start time of the simulation 
actions = ['PSZACcontroller_oveHeaPer1_u']
kpi_zones = ["1"]
building_obs = ['senHouDec_y','senTemRoom1_y']
forecast_obs = {'TDryBul':[0,1],'HGloHor':[0]}
KPI_rewards = {
    "ener_tot": {"hyper": -20, "power": 1},
    "tdis_tot": {"hyper": -45, "power": 1},
    "idis_tot": {"hyper": 0, "power": 1},
    "cost_tot": {"hyper": 0, "power": 1},
    "emis_tot": {"hyper": 0, "power": 1},
    "power_pen":{"hyper":-1,  "power":1}}
# --------------------
# --------------------

env = BoptestGymEnv(episode_length=episode_length,
                     Ts=step,
                     start_time=start_time,
                     actions=actions,
                     building_obs=building_obs,
                     forecast_obs=forecast_obs,
                     kpi_zones= kpi_zones,
                     password = None,  # put your own password
                     lower_obs_bounds=[0,  286, 286, 286,     0],
                     upper_obs_bounds=[24, 303, 303, 303,  1000],
                     KPI_rewards=KPI_rewards,
                     n_obs = False)

kpi_list = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']
state_size = env.observation_space.shape[0]

print ("State_size :{}".format(state_size))

episodes= 6
last_ep= 0

Agent_1 = DQN_Agent(state_size, 4)

# RUN TEST CASE - From 2nd episode
# -------------

mem_list_1 = []
Historian = {key: [] for key in ['time', 'states', 'rewards', 'episodes', 'action_1','senTemOA_y',
                                 'senTRoom_y','senTRoom1_y','senTRoom2_y','senTRoom3_y','senTRoom4_y',
                                 'Total_Pow_Dem_0','Total_Pow_Dem_1','Total_Pow_Dem_2','Total_Pow_Dem_3','Total_Pow_Dem_4',
                                 'Heating_Pow_Dem_0','Heating_Pow_Dem_1','Heating_Pow_Dem_2','Heating_Pow_Dem_3','Heating_Pow_Dem_4',
                                 'Cooling_Pow_Dem_0','Cooling_Pow_Dem_1','Cooling_Pow_Dem_2','Cooling_Pow_Dem_3','Cooling_Pow_Dem_4',
                                 'Zone_1_HC_Action','Damper_0','Damper_1','Damper_2','Damper_3','Damper_4']}

KPI_hist = {key: [] for key in kpi_list}
KPI_hist['episodes'] = []
KPI_hist['scores'] = []
# --------------------
print ("Agent memory")
print (len(Agent_1.memory))



print('\nRunning controller script...')


# Simulation Loop
for e in range(last_ep,last_ep+episodes):
    Agent_1.update_target_model()  # From 2nd episode
    score = 0
    e = e + 1
    print('\nRunning controller script...')
    state = env.reset()  # check if the reset function resets the weights as well

    print ("State")
    print (state)

    print("Modified State")
    print(state)

    state = np.reshape(state, [1, state_size])    
    counter = 0

    for i in range(int(episode_length/step)):
        print("episode")
        print(e)
        print("Time Step")
        print(step)       

        print("Agent Memory")
        print(len(Agent_1.memory))
        counter= counter + 1

        abs_time = i * step
        minutes = ((abs_time) % 3600) / 60
        days = math.floor(abs_time / (3600 * 24))

        building_states = env.get_building_states()
        hou_min = building_states['senHouDec_y']


        print('Days: {}, Hours: {} , Minutes: {}'.format(days,hou_min, minutes))
        raw_action_u1 = Agent_1.get_action(state)
        q_1 = Agent_1.target_predict_qvalue(state)
        
        print("Raw Action")
        print(raw_action_u1)

        action_proc= [0,0.1,0.15,0.25]
        act = (action_proc[raw_action_u1])

        processed_act = [act]

        print()
        print("Heating Coil Action")
        print(processed_act)

        print("Q-values_1")
        print(q_1)

        next_state, reward, done, info = env.step(processed_act)
        score += reward


        next_state = np.reshape(next_state, [1, state_size])

        building_states = env.get_building_states()

        # Get Power
        print("Total Power;  Zone 0:{}, Zone 1:{}, Zone 2: {}, Zone 3: {}, Zone 4; {}".format(
            round(building_states['senPowCor_y'], 2),
            round(building_states['senPowPer1_y'], 2),
            round(building_states['senPowPer2_y'], 2),
            round(building_states['senPowPer3_y'], 2),
            round(building_states['senPowPer4_y'], 2)))

        
        print()
        

        # Append samples
        Agent_1.append_sample(state, raw_action_u1, reward, next_state, done)

        if (counter%24*3)==0:
            # Train Models
            Agent_1.train_model()


        if (counter%24*5)==0:
            # Train Models
            print ("Updating target NN")
            Agent_1.update_target_model()  # From 2nd episode

        mem_list_1.append((state, raw_action_u1, reward, next_state, done))  # 1st episode



        state = next_state

        print('Days: {}, Hours: {} , Minutes: {}'.format(days, hou_min, minutes))
        print(next_state, reward, done, info)

        print("Room Temperature;  Zone 0: {}, Zone 1: {}, Zone 2: {}, Zone 3: {}, Zone 4: {}, OA Temp: {}".format(
            building_states['senTemRoom_y'],
            building_states['senTemRoom1_y'],
            building_states['senTemRoom2_y'],
            building_states['senTemRoom3_y'],
            building_states['senTemRoom4_y'],
            building_states['senTemOA_y']))



        print("Exploration")
        print (Agent_1.exploration_value())

        u=env.get_input_hist()

        print("Score")
        print(score)

        print("\n")

        Historian["time"].append(i * step)
        Historian["states"].append(state[0])
        Historian["episodes"].append(e)
        Historian["rewards"].append(reward)
        Historian["action_1"].append(processed_act[0])
        Historian['senTemOA_y'].append(building_states['senTemOA_y'])

        Historian["senTRoom_y"].append(building_states['senTemRoom_y'])
        Historian["senTRoom1_y"].append(building_states['senTemRoom1_y'])
        Historian['senTRoom2_y'].append(building_states['senTemRoom2_y'])
        Historian['senTRoom3_y'].append(building_states['senTemRoom3_y'])
        Historian['senTRoom4_y'].append(building_states['senTemRoom4_y'])

        Historian["Total_Pow_Dem_0"].append(building_states['senPowCor_y'])
        Historian["Total_Pow_Dem_1"].append(building_states['senPowPer1_y'])
        Historian["Total_Pow_Dem_2"].append(building_states['senPowPer2_y'])
        Historian["Total_Pow_Dem_3"].append(building_states['senPowPer3_y'])
        Historian["Total_Pow_Dem_4"].append(building_states['senPowPer4_y'])

        Historian["Heating_Pow_Dem_0"].append(building_states['senHeaPow_y'])
        Historian["Heating_Pow_Dem_1"].append(building_states['senHeaPow1_y'])
        Historian["Heating_Pow_Dem_2"].append(building_states['senHeaPow2_y'])
        Historian["Heating_Pow_Dem_3"].append(building_states['senHeaPow3_y'])
        Historian["Heating_Pow_Dem_4"].append(building_states['senHeaPow4_y'])

        Historian["Cooling_Pow_Dem_0"].append(building_states['senCCPow_y'])
        Historian["Cooling_Pow_Dem_1"].append(building_states['senCCPow1_y'])
        Historian["Cooling_Pow_Dem_2"].append(building_states['senCCPow2_y'])
        Historian["Cooling_Pow_Dem_3"].append(building_states['senCCPow3_y'])
        Historian["Cooling_Pow_Dem_4"].append(building_states['senCCPow4_y'])

        Historian["Zone_1_HC_Action"].append(u['PSZACcontroller_oveHeaPer1_u'])

        Historian['Damper_0'].append(u['PSZACcontroller_oveDamCor_u'])
        Historian['Damper_1'].append(u['PSZACcontroller_oveDamP1_u'])
        Historian['Damper_2'].append(u['PSZACcontroller_oveDamP2_u'])
        Historian['Damper_3'].append(u['PSZACcontroller_oveDamP3_u'])
        Historian['Damper_4'].append(u['PSZACcontroller_oveDamP4_u'])


    # Print KPIs
    kpi = (env.get_KPIs())

    for kpi_name in kpi_list:
        KPI_hist[kpi_name].append(kpi[kpi_name])
    KPI_hist['episodes'].append(e)
    KPI_hist['scores'].append(score)
    print("Agent Memory")
    print(len(Agent_1.memory))

    KPI_df = pd.DataFrame.from_dict(KPI_hist)
    KPI_df.to_csv("RL_Data_test/01_KPI/dr_KPI_v2_" + str(e) + ".csv")

    df_m_1 = pd.DataFrame(mem_list_1, columns=['States', 'Action', 'Reward', 'Next_State', 'Done'])
    df_m_1.to_csv("RL_Data_test/04_Mem/dr_mem_data_v2_" + str(e) + ".csv")

    Agent_1.model_save_weights("RL_Data_test/02_NN/dr_DQN_v2_" + str(e) + ".h5")

    Historian_df = pd.DataFrame.from_dict(Historian)
    Historian_df.to_csv("RL_Data_test/RL_Agent/dr_data_test_v2_" + str(e) + ".csv")


print('\nTest case complete.')
# -------------


# POST PROCESS RESULTS
# --------------------
# Get result data

res = requests.get('{0}/results'.format(url)).json()

print("Agent Memory")
print(len(Agent_1.memory))
env.print_KPIs()
