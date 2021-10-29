
# GENERAL PACKAGE IMPORT
# ----------------------
import requests
import numpy as np;import pandas as pd
import json,collections
from DQN_Agent_Dey_v4 import DQN_Agent

from boptestGymEnv_DR_v2 import BoptestGymEnv,DiscretizedActionWrapper
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
url = 'http://127.0.0.1:5000'


# ---------------
#actions = [0.0 for ]
start = time.time()

# GET TEST INFORMATION
# --------------------


step = 300
episode_length = 3600*24*1
start_time=24*3600*186
actions = ['oveCooSet_u','oveCooSet1_u','oveCooSet2_u','oveCooSet3_u','oveCooSet4_u']
kpi_zones = ["0","1","2","3","4"]
building_obs = ['senTRoom_y','senTRoom1_y','senTRoom2_y','senTRoom3_y','senTRoom4_y','senHouDec_y']
dr_obs = [0,1.25]
forecast_obs = {}
KPI_rewards = {
    "ener_tot": {"hyper": -1, "power": 1},
    "tdis_tot": {"hyper": -1, "power": 1},
    "idis_tot": {"hyper": 0, "power": 1},
    "cost_tot": {"hyper": 0, "power": 1},
    "emis_tot": {"hyper": 0, "power": 1},
    "power_pen":{"hyper":-1,  "power":1}}
# --------------------
# --------------------

# Define customized KPI if any

customizedkpis=[] # Initialize customzied kpi calculation list

env = BoptestGymEnv(max_episode_length=episode_length,
                                             Ts=step,
                                             start_time=start_time,
                                             actions=actions,
                                             building_obs=building_obs,
                                             forecast_obs=forecast_obs,
                                             dr_obs = dr_obs,
                                             kpi_zones= kpi_zones,
                                             dr_power_limit= 6000, # in watts
                                             DR_event = True,
                                             DR_time = [3600*14,3600*16],
                                             lower_obs_bounds=[286, 286, 286, 286, 286,  0,  0, 0],
                                             upper_obs_bounds=[303, 303, 303, 303, 303, 24,  1, 1],
                                             KPI_rewards=KPI_rewards,
                                             n_obs = True,
                                             dr_all_time = True)
kpi_list = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']
state_size = env.observation_space.shape[0]-4


episodes= 100
last_ep= 14

Agent_1 = DQN_Agent(state_size, 2)

# RUN TEST CASE - From 2nd episode
# -------------

if last_ep == 0:
    mem_list_1 = []
else:
    mem_list_1 = pd.read_csv("data_dqn_dr/04_Mem/dr_mem_data_v2_" + str(last_ep) + ".csv", dtype=object)
    mem_list_1.drop(mem_list_1.columns[0], axis=1, inplace=True)
    mem_list_1['Action'] = mem_list_1['Action'].astype('float')
    mem_list_1['Reward'] = mem_list_1['Reward'].astype('float')
    mem_list_1['States'] = mem_list_1['States'].map(
        lambda x: " ".join((x.strip('[').strip(']').replace("\n", "")).split()))
    mem_list_1['States'] = mem_list_1['States'].map(
        lambda x: np.reshape(np.array(x.split(' '), dtype=np.float32), (1, -1)))
    mem_list_1['Next_State'] = mem_list_1['Next_State'].map(
        lambda x: " ".join((x.strip('[').strip(']').replace("\n", "")).split()))
    mem_list_1['Next_State'] = mem_list_1['Next_State'].map(
        lambda x: np.reshape(np.array(x.split(' '), dtype=np.float32), (1, -1)))

    for i in range(len(mem_list_1)):
        state_m1 = mem_list_1.iloc[i][0];
        action_m1 = mem_list_1.iloc[i][1]
        reward_m1 = mem_list_1.iloc[i][2];
        next_state_m1 = mem_list_1.iloc[i][3];
        done_m1 = mem_list_1.iloc[i][4]
        Agent_1.append_sample(state_m1, action_m1, reward_m1, next_state_m1, done_m1)

    Agent_1.model_load_weights("data_dqn_dr/02_NN/DQN_0_" + str(last_ep) + ".h5")  # From 2nd episode


start = time.time()

Historian = {key: [] for key in ['time', 'states', 'rewards', 'episodes', 'action_1','dr_start','dr_end',
                                 'reward_energy','reward_tdisc','reward_power','senTemOA_y',
                                 'senTRoom_y','senTRoom1_y','senTRoom2_y','senTRoom3_y','senTRoom4_y',
                                 'Total_Pow_Dem_0','Total_Pow_Dem_1','Total_Pow_Dem_2','Total_Pow_Dem_3','Total_Pow_Dem_4',
                                 'Heating_Pow_Dem_0','Heating_Pow_Dem_1','Heating_Pow_Dem_2','Heating_Pow_Dem_3','Heating_Pow_Dem_4',
                                 'Cooling_Pow_Dem_0','Cooling_Pow_Dem_1','Cooling_Pow_Dem_2','Cooling_Pow_Dem_3','Cooling_Pow_Dem_4',
                                 'oveHCSet_u', 'oveHCSet_activate', 'oveHCSet1_u', 'oveHCSet1_activate', 'oveHCSet2_u',
                                 'oveHCSet2_activate', 'oveHCSet3_u', 'oveHCSet3_activate', 'oveHCSet4_u','oveHCSet4_activate',
                                 'oveCC_u', 'oveCC_activate', 'oveCC1_u', 'oveCC1_activate', 'oveCC2_u','oveCC2_activate', 'oveCC3_u',
                                 'oveCC3_activate', 'oveCC4_u', 'oveCC4_activate', 'oveDSet_u', 'oveDSet_activate','oveDSet1_u',
                                 'oveDSet1_activate', 'oveDSet2_u', 'oveDSet2_activate', 'oveDSet3_u',
                                 'oveDSet3_activate','oveDSet4_u', 'oveDSet4_activate', 'oveVFRSet_u', 'oveVFRSet_activate', 'oveVFRSet1_u',
                                 'oveVFRSet1_activate','oveVFRSet2_u', 'oveVFRSet2_activate', 'oveVFRSet3_u', 'oveVFRSet3_activate',
                                 'oveVFRSet4_u','oveVFRSet4_activate','Zone_1_HC_SP']}

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

    mean_temp = (state[0]+state[1]+state[2]+state[3]+state[4])/5
    state = np.array([mean_temp,state[5],state[6],state[7]]).astype(np.float32)
    print("Modified State")
    print(state)

    state = np.reshape(state, [1, state_size])
    dr_rand_start = random.uniform(13, 15)
    dr_rand_end = dr_rand_start + random.uniform(1, 1.5)
    DR_time = [3600 * dr_rand_start, 3600 * dr_rand_end]
    env.set_DR_time(DR_time)
    counter = 0


    for i in range(int(episode_length/step)):
        print("episode")
        print(e)
        print("Time Step")
        print(step)
        print("DR_Time")
        print(dr_rand_start)
        print("DR_End_time")
        print(DR_time[1] / 3600)

        print("Agent Memory")
        print(len(Agent_1.memory))
        counter= counter + 1

        abs_time = i * step
        #print(abs_time)
        minutes = ((abs_time) % 3600) / 60
        days = math.floor(abs_time / (3600 * 24))


        building_states = env.get_building_states()

        hou_min = building_states['senHouDec_y']



        if (hou_min >= dr_rand_start) & (hou_min < (dr_rand_end)):
            print("First Condition")
            w = [0.0, 0.5, 0.5]
            env.change_dr_limit(6000)
        else:
            print("Second Condition")
            w = [0.2, 0.7, 0.1]
            env.change_dr_limit(24000)

        print(w)



        price = {'energy': 0.0589 * 100, 't_disc': 0.010112 * 100, 'dr_price': 7.89 / 1000 * 100}


        occupancy = building_states['senOcc_y'] + building_states['senOcc1_y'] + building_states['senOcc2_y'] + \
                    building_states['senOcc3_y'] + building_states['senOcc4_y']

        # if (hours >= 0) & (hours < 6):
        #     occupancy = 0
        # elif (hours >= 6) & (hours < 8):
        #     occupancy = 5.49
        # elif (hours >= 8) & (hours < 12):
        #     occupancy = 26.0775
        # elif (hours >= 12) & (hours < 13):
        #     occupancy = 13.725
        # elif (hours >= 13) & (hours < 17):
        #     occupancy = 26.0775
        # elif (hours >= 17) & (hours < 18):
        #     occupancy = 8.235
        # elif (hours >= 18) & (hours < 20):
        #     occupancy = 2.745
        # elif (hours >= 20) & (hours < 24):
        #     occupancy = 1.3725


        print("Occupancy")
        print(occupancy)

        # w = [1,1,1]
        KPI_rewards = {
            "ener_tot": {"hyper": -price['energy'] * w[0], "power": 1},
            "tdis_tot": {"hyper": -price['t_disc'] * w[1] * occupancy, "power": 1},
            "idis_tot": {"hyper": 0, "power": 1},
            "cost_tot": {"hyper": 0, "power": 1},
            "emis_tot": {"hyper": 0, "power": 1},
            "power_pen": {"hyper": -price['dr_price'] * w[2], "power": 1}}

        env.change_rewards_weights(KPI_rewards)

        print('Days: {}, Hours: {} , Minutes: {}'.format(days,hou_min, minutes))
        raw_action_u1 = Agent_1.get_action(state)
        q_1 = Agent_1.target_predict_qvalue(state)

        # if state[0][3]==1:
        #     raw_action_u1 = 1


        if abs(dr_rand_start - hou_min) < 1 * step / 3600:
            raw_action_u1 = 0

        print ("Mean temp")
        print (mean_temp)


        #
        # if (hou_min<7.5)or(hou_min)>17:
        #     if (mean_temp*(303-286)+286)<298:
        #         print ("Overriding")
        #         raw_action_u1=0
        #
        #
        # if (hou_min>7.5)or(hou_min)<9.5:
        #     if (mean_temp*(303-286)+286)>299:
        #         print ("Overriding")
        #         raw_action_u1=1



        print("Raw Action")
        print(raw_action_u1)

        action_proc = [33 + 273.15, 19.5 + 273.15]
        act = (action_proc[raw_action_u1])

        processed_act = [act, act, act, act, act]

        print()
        print("Cooling Coil Setpoint Action")
        print(processed_act)

        print("Q-values_1")
        print(q_1)

        next_state, reward, done, info = env.step(processed_act)
        score += reward

        mean_temp = (next_state[0] + next_state[1] + next_state[2] + next_state[3] + next_state[4])/5

        next_state = np.array([mean_temp, next_state[5], next_state[6], next_state[7]]).astype(np.float32)
        next_state = np.reshape(next_state, [1, state_size])


        individual_rewards = env.get_individual_rewards()
        print("Individual Rewards")
        print(individual_rewards)

        building_states = env.get_building_states()

        # Get Power
        print("Total Power;  Zone 0:{}, Zone 1:{}, Zone 2: {}, Zone 3: {}, Zone 4; {}".format(
            round(building_states['senPowCor_y'], 2),
            round(building_states['senPowPer1_y'], 2),
            round(building_states['senPowPer2_y'], 2),
            round(building_states['senPowPer3_y'], 2),
            round(building_states['senPowPer4_y'], 2)))

        t_pow = building_states['senPowCor_y'] + building_states['senPowPer1_y'] + building_states['senPowPer2_y'] + \
                building_states['senPowPer3_y'] + building_states['senPowPer4_y']
        print()
        print("Total Power of all Zones: {}".format(t_pow))
        print("Mean temp: {}".format(mean_temp))


        # Append samples
        Agent_1.append_sample(state, raw_action_u1, reward, next_state, done)


        if (counter%24*3)==0:
            # Train Models
            Agent_1.train_model()


        if (counter%24*5)==0:
            # Train Models
            print ("Updating target NN")
            Agent_1.update_target_model()  # From 2nd episode

        if last_ep == 0:
            # Append List for buffer memory
            mem_list_1.append((state, raw_action_u1, reward, next_state, done))  # 1st episode
        else:
            # Append List for buffer memory
            mem_list_1 = mem_list_1.append(
                {'States': state, 'Action': raw_action_u1, 'Reward': reward, 'Next_State': next_state, 'Done': done},
                ignore_index=True)  # From 2nd episode



        state = next_state

        print('Days: {}, Hours: {} , Minutes: {}'.format(days, hou_min, minutes))
        print(next_state, reward, done, info)

        print("Room Temperature;  Zone 0: {}, Zone 1: {}, Zone 2: {}, Zone 3: {}, Zone 4: {}, OA Temp: {}".format(
            building_states['senTRoom_y'],
            building_states['senTRoom1_y'],
            building_states['senTRoom2_y'],
            building_states['senTRoom3_y'],
            building_states['senTRoom4_y'],
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
        Historian["dr_start"].append(dr_rand_start)
        Historian["dr_end"].append(DR_time[1] / 3600)
        Historian['senTemOA_y'].append(building_states['senTemOA_y'])

        Historian["senTRoom_y"].append(building_states['senTRoom_y'])
        Historian["senTRoom1_y"].append(building_states['senTRoom1_y'])
        Historian['senTRoom2_y'].append(building_states['senTRoom2_y'])
        Historian['senTRoom3_y'].append(building_states['senTRoom3_y'])
        Historian['senTRoom4_y'].append(building_states['senTRoom4_y'])

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

        Historian["oveHCSet_u"].append(u['oveHCSet_u'])
        Historian["oveHCSet1_u"].append(u['oveHCSet1_u'])
        Historian["oveHCSet2_u"].append(u['oveHCSet2_u'])
        Historian["oveHCSet3_u"].append(u['oveHCSet3_u'])
        Historian["oveHCSet4_u"].append(u['oveHCSet4_u'])

        Historian['reward_energy'].append(individual_rewards['Energy'])
        Historian['reward_tdisc'].append(individual_rewards['Thermal_Discomfort'])
        Historian['reward_power'].append(individual_rewards['Power_Penalty'])

        Historian['oveHCSet_activate'].append(u['oveHCSet_activate'])
        Historian['oveHCSet1_activate'].append(u['oveHCSet1_activate'])
        Historian['oveHCSet2_activate'].append(u['oveHCSet2_activate'])
        Historian['oveHCSet3_activate'].append(u['oveHCSet3_activate'])
        Historian['oveHCSet4_activate'].append(u['oveHCSet4_activate'])

        Historian['oveCC_u'].append(u['oveCC_u'])
        Historian['oveCC1_u'].append(u['oveCC1_u'])
        Historian['oveCC2_u'].append(u['oveCC2_u'])
        Historian['oveCC3_u'].append(u['oveCC3_u'])
        Historian['oveCC4_u'].append(u['oveCC4_u'])

        Historian['oveCC_activate'].append(u['oveCC_activate'])
        Historian['oveCC1_activate'].append(u['oveCC1_activate'])
        Historian['oveCC2_activate'].append(u['oveCC2_activate'])
        Historian['oveCC3_activate'].append(u['oveCC3_activate'])
        Historian['oveCC4_activate'].append(u['oveCC4_activate'])

        Historian['oveDSet_u'].append(u['oveDSet_u'])
        Historian['oveDSet1_u'].append(u['oveDSet1_u'])
        Historian['oveDSet2_u'].append(u['oveDSet2_u'])
        Historian['oveDSet3_u'].append(u['oveDSet3_u'])
        Historian['oveDSet4_u'].append(u['oveDSet4_u'])

        Historian['oveDSet_activate'].append(u['oveDSet_activate'])
        Historian['oveDSet1_activate'].append(u['oveDSet1_activate'])
        Historian['oveDSet2_activate'].append(u['oveDSet2_activate'])
        Historian['oveDSet3_activate'].append(u['oveDSet3_activate'])
        Historian['oveDSet4_activate'].append(u['oveDSet4_activate'])

        Historian['oveVFRSet_u'].append(u['oveVFRSet_u'])
        Historian['oveVFRSet1_u'].append(u['oveVFRSet1_u'])
        Historian['oveVFRSet2_u'].append(u['oveVFRSet2_u'])
        Historian['oveVFRSet3_u'].append(u['oveVFRSet3_u'])
        Historian['oveVFRSet4_u'].append(u['oveVFRSet4_u'])

        Historian['oveVFRSet_activate'].append(u['oveVFRSet_activate'])
        Historian['oveVFRSet1_activate'].append(u['oveVFRSet1_activate'])
        Historian['oveVFRSet2_activate'].append(u['oveVFRSet2_activate'])
        Historian['oveVFRSet3_activate'].append(u['oveVFRSet3_activate'])
        Historian['oveVFRSet4_activate'].append(u['oveVFRSet4_activate'])

        Historian['Zone_1_HC_SP'].append(u['oveHeaSet1_u'])
    # Print KPIs
    kpi = (env.get_KPIs())

    for kpi_name in kpi_list:
        KPI_hist[kpi_name].append(kpi[kpi_name])
    KPI_hist['episodes'].append(e)
    KPI_hist['scores'].append(score)
    print("Agent Memory")
    print(len(Agent_1.memory))

    KPI_df = pd.DataFrame.from_dict(KPI_hist)
    KPI_df.to_csv("data_dqn_dr/01_KPI/dr_KPI_v2_" + str(e) + ".csv")

    df_m_1 = pd.DataFrame(mem_list_1, columns=['States', 'Action', 'Reward', 'Next_State', 'Done'])
    df_m_1.to_csv("data_dqn_dr/04_Mem/dr_mem_data_v2_" + str(e) + ".csv")

    Agent_1.model_save_weights("data_dqn_dr/02_NN/dr_DQN_v2_" + str(e) + ".h5")

    Historian_df = pd.DataFrame.from_dict(Historian)
    Historian_df.to_csv("data_dqn_dr/dr_data_test_v2_" + str(e) + ".csv")


print('\nTest case complete.')
# -------------


# POST PROCESS RESULTS
# --------------------
# Get result data

res = requests.get('{0}/results'.format(url)).json()


print("Agent Memory")
print(len(Agent_1.memory))
env.print_KPIs()
