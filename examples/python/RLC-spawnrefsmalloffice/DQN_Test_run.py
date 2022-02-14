import numpy as np;import pandas as pd
from DQN_Agent_test import DQN_Agent
from pathlib import Path; from RL_functions import *
import sys
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'openai-gym'))
from boptestGymEnv import BoptestGymEnv
import math
import matplotlib.pyplot as plt


# --------------------
# Set parameters for initializing the gym environment


actions = ['PSZACcontroller_oveHeaPer1_u']     # Specify which control actions to actuate by specifying the keys
kpi_zones = ["1"]                              # Select which zone KPI to be included in the reward function

''' Form the Observation States  '''
building_obs = ['senTemRoom1_y','senHouDec_y']   # Specify which building sensor states to return as observation States
forecast_obs = {'TDryBul':[0],'HGloHor':[0]}   # Specify which exogenous states to return as observation States - 0: index means current, 1: index means forecasted state 1 hour ahead

# Set the weights for the different KPIs to form the reward function
KPI_rewards = {
    "ener_tot": {"hyper": -120, "power": 1},
    "tdis_tot": {"hyper": -160, "power": 1},
    "idis_tot": {"hyper":   0, "power": 1},
    "cost_tot": {"hyper":   0, "power": 1},
    "emis_tot": {"hyper":   0, "power": 1},
    "power_pen":{"hyper":   0, "power": 1}}      # mainly used for DR power penalty
# --------------------




kpi_list = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']


episodes= 1
last_ep= 120

Historian = {key: [] for key in ['time', 'states', 'rewards', 'episodes', 'action_1','senTemOA_y','day_no',
                                 'senTRoom_y','senTRoom1_y','senTRoom2_y','senTRoom3_y','senTRoom4_y',
                                 'Total_Pow_Dem_0','Total_Pow_Dem_1','Total_Pow_Dem_2','Total_Pow_Dem_3','Total_Pow_Dem_4',
                                 'Heating_Pow_Dem_0','Heating_Pow_Dem_1','Heating_Pow_Dem_2','Heating_Pow_Dem_3','Heating_Pow_Dem_4',
                                 'Cooling_Pow_Dem_0','Cooling_Pow_Dem_1','Cooling_Pow_Dem_2','Cooling_Pow_Dem_3','Cooling_Pow_Dem_4',
                                 'Zone_1_HC_Action']}


#'Damper_0','Damper_1','Damper_2','Damper_3','Damper_4'
KPI_hist = {key: [] for key in kpi_list}
KPI_hist['episodes'] = []
KPI_hist['scores'] = []
KPI_hist['day_no'] = []
# --------------------


print('\n Starting Simulation...')

zonetemp = []
heatingcoil = []


# Simulation Loop
for e in range(last_ep,last_ep+episodes):
    # Initialize the environment
    day_no =  3
    start_time = 24 * 3600 * day_no  # Specify the start time of the simulation
    step = 300
    episode_length = 3600 * 1 * 24  # Set the simulation length in seconds

    env = BoptestGymEnv(episode_length=episode_length,
                        testcase='spawnrefsmalloffice',
                        Ts=step,
                        start_time=start_time,
                        actions=actions,
                        building_obs=building_obs,
                        forecast_obs=forecast_obs,
                        kpi_zones=kpi_zones,
                        lower_obs_bounds=[273.15 + 15, 0, -12, 0],  # manually set the lower bounds for observation
                        upper_obs_bounds=[273.15 + 27, 24, 5, 195.8],  # manually set the upper bounds for observation
                        KPI_rewards=KPI_rewards,
                        n_obs=True)  # if set to True returns a normalized state vector between 0-1

    state_size = env.observation_space.shape[0]

    # Initializing the RL Agent
    Agent_1 = DQN_Agent(state_size, 5)
    print("State_size :{}".format(state_size))

    # loading previous memory buffer
    if last_ep == 0:
        mem_list_1 = []
    else:
        mem_list_1 = mem_processor(filename="RL_Data_test/04_Mem/mem_data_" + str(e) + ".csv")
        for i in range(len(mem_list_1)):
            state_m1 = mem_list_1.iloc[i][0];
            action_m1 = mem_list_1.iloc[i][1];
            reward_m1 = mem_list_1.iloc[i][2];
            next_state_m1 = mem_list_1.iloc[i][3];
            done_m1 = mem_list_1.iloc[i][4]
            Agent_1.append_sample(state_m1, action_m1, reward_m1, next_state_m1, done_m1)

    print ("loading weights")
    Agent_1.model_load_weights("RL_Data_test/02_NN/DQN_" + str(e) + ".h5")  # From 2nd episode
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
        print("Day:{}".format(day_no))
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

        building_states = env.get_building_states()  # returns a dictionary of all the current states of the building sensors
        hou_min = building_states['senHouDec_y']


        print('Days: {}, Hours: {} , Minutes: {}'.format(days,hou_min, minutes))
        raw_action_u1 = Agent_1.get_action(state)
        q_1 = Agent_1.target_predict_qvalue(state)

        print("Raw Action")
        print(raw_action_u1)

        action_proc= [0,0.05,0.15,0.25,0.45]


        processed_act = [action_proc[raw_action_u1]]

        print()
        print("Heating Coil Action")
        print(processed_act)

        print("Q-values_1")
        print(q_1)

        next_state, reward, done, info = env.step(processed_act)
        score += reward

        next_state = np.reshape(next_state, [1, state_size])
        building_states = env.get_building_states()

        if counter % (12) == 0:
            Agent_1.train_model()

        if counter % (12 * 4) == 0:
            Agent_1.update_target_model()

        weather_states = env.get_weather_forecast()

        print ("Dry bulb temp: {}".format(weather_states['TDryBul'][0]))

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

        if last_ep == 0:
            mem_list_1.append((state, raw_action_u1, reward, next_state, done))  # 1st episode
        else:
            mem_list_1 = mem_list_1.append(
                {'States': state, 'Action': raw_action_u1, 'Reward': reward, 'Next_State': next_state, 'Done': done},
                ignore_index=True)

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

        print ("Forecasts")
        print (env.get_forecasts())


        print("Exploration")
        print (Agent_1.exploration_value())

        u=env.get_input_hist()

        print("Score")
        print(score)

        print("\n")

        # Store Data
        Historian["time"].append(i * step)
        Historian["states"].append(state[0])
        Historian["episodes"].append(e)
        Historian["rewards"].append(reward)
        Historian["action_1"].append(processed_act[0])
        Historian['senTemOA_y'].append(building_states['senTemOA_y'])
        Historian['day_no'].append(day_no)

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

        zonetemp.extend([building_states['senTemRoom1_y'] - 273.15])
        heatingcoil.extend([building_states['senPowPer1_y']])



    # Print KPIs
    kpi = (env.get_KPIs())

    for kpi_name in kpi_list:
        KPI_hist[kpi_name].append(kpi[kpi_name])
    KPI_hist['episodes'].append(e)
    KPI_hist['scores'].append(score)
    KPI_hist['day_no'].append(day_no)
    print("Agent Memory : {}".format(len(Agent_1.memory)))

    KPI_df = pd.DataFrame.from_dict(KPI_hist)
    KPI_df.to_csv("RL_Data_test/01_KPI/dr_KPI_v2_" + str(e) + ".csv")

    df_m_1 = pd.DataFrame(mem_list_1, columns=['States', 'Action', 'Reward', 'Next_State', 'Done'])
    df_m_1.to_csv("RL_Data_test/04_Mem/mem_data_" + str(e) + ".csv")

    Historian_df = pd.DataFrame.from_dict(Historian)
    Historian_df.to_csv("RL_Data_test/dr_data_test_v2_" + str(e) + ".csv")
    Agent_1.model_save_weights("RL_Data_test/02_NN/DQN_" + str(e) + ".h5")

    env.print_KPIs()




print('\nTest case complete.')
# --------------------
# Get result data





