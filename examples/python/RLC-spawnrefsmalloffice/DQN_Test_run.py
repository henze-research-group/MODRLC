import numpy as np;import pandas as pd
from DQN_Agent_test import DQN_Agent
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'openai-gym'))
from boptestGymEnv import BoptestGymEnv
import math
import matplotlib.pyplot as plt


def plot(zonetemp, heatingcoil, Historian, axes, plotutils):

    time_hours = [time / 3600 for time in Historian["time"]]
    axes[0].cla()
    axes[1].cla()
    axes[0].set_title('Zone temperature', fontweight='bold')
    axes[0].set_ylim(15, 27)
    axes[0].set_xlim(0, plotutils['length'] / 3600)
    axes[0].set_xticks(range(0, int(plotutils['length'] / 3600) + 6, 6))
    axes[0].set_ylabel('Temperature [C]')
    axes[0].set_yticks([i for i in range(15, 28)])
    axes[0].grid(which='both', linewidth=0.5, color='white')
    axes[0].set_facecolor("gainsboro")

    axes[1].set_title('Heating coil power demand (thermal)', fontweight='bold')
    axes[1].set_ylim(0, 15000)
    axes[1].set_xlim(0, plotutils['length'] / 3600)
    axes[1].set_xticks(range(0, int(plotutils['length'] / 3600) + 6, 6))
    axes[1].set_ylabel('Watts [W]')
    axes[1].set_xlabel('Time [hours]')
    axes[1].set_yticks([i for i in range(0, 16000, 1000)])
    axes[1].grid(which='both', linewidth=0.5, color='white')
    axes[1].set_facecolor("gainsboro")

    axes[0].plot(plotutils['time'], plotutils['lostp'], color='red', ls='--', label='Setpoints')
    axes[0].plot(plotutils['time'], plotutils['histp'], color='red', ls='--')
    axes[0].plot(time_hours, zonetemp, label='Zone temperature')
    axes[1].plot(time_hours, heatingcoil)
    axes[0].legend(loc='upper right')
    plt.tight_layout()
    plt.draw()
    plt.pause(0.5)

# --------------------
# Set parameters for initializing the gym environment

step = 300
episode_length = 3600*1*24                    # Set the simulation length in seconds
day_no = 1  #np.random.choice([1,3,4,5,8,9,10])
start_time=24*3600*day_no                 # Specify the start time of the simulation
actions = ['PSZACcontroller_oveHeaPer1_u']     # Specify which control actions to actuate by specifying the keys
kpi_zones = ["1"]                              # Select which zone KPI to be included in the reward function

''' Form the Observation States  '''
building_obs = ['senTemRoom1_y','senHouDec_y']   # Specify which building sensor states to return as observation States
forecast_obs = {'TDryBul':[0],'HGloHor':[0]}   # Specify which exogenous states to return as observation States - 0: index means current, 1: index means forecasted state 1 hour ahead

# Set the weights for the different KPIs to form the reward function
KPI_rewards = {
    "ener_tot": {"hyper": -60, "power": 1},
    "tdis_tot": {"hyper": -80, "power": 1},
    "idis_tot": {"hyper":   0, "power": 1},
    "cost_tot": {"hyper":   0, "power": 1},
    "emis_tot": {"hyper":   0, "power": 1},
    "power_pen":{"hyper":   0, "power": 1}}      # mainly used for DR power penalty
# --------------------


# Initiliaze the environment
env = BoptestGymEnv(episode_length=episode_length,
                    testcase='spawnrefsmalloffice',
                     Ts=step,
                     start_time=start_time,
                     actions=actions,
                     building_obs=building_obs,
                     forecast_obs=forecast_obs,
                     kpi_zones= kpi_zones,
                     password = None,                                         # put your own password
                     lower_obs_bounds=[273.15+15,  0, -12,      0],    # manually set the lower bounds for observation
                     upper_obs_bounds=[273.15+27, 24,  5,    195.8],    # manually set the upper bounds for observation
                     KPI_rewards=KPI_rewards,
                     n_obs = True)                              # if set to True returns a normalized state vector between 0-1

kpi_list = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']
state_size = env.observation_space.shape[0]

print ("State_size :{}".format(state_size))

episodes= 20
last_ep= 6

Agent_1 = DQN_Agent(state_size, 5)


# RUN TEST CASE -
# -------------


Historian = {key: [] for key in ['time', 'states', 'rewards', 'episodes', 'action_1','senTemOA_y',
                                 'senTRoom_y','senTRoom1_y','senTRoom2_y','senTRoom3_y','senTRoom4_y',
                                 'Total_Pow_Dem_0','Total_Pow_Dem_1','Total_Pow_Dem_2','Total_Pow_Dem_3','Total_Pow_Dem_4',
                                 'Heating_Pow_Dem_0','Heating_Pow_Dem_1','Heating_Pow_Dem_2','Heating_Pow_Dem_3','Heating_Pow_Dem_4',
                                 'Cooling_Pow_Dem_0','Cooling_Pow_Dem_1','Cooling_Pow_Dem_2','Cooling_Pow_Dem_3','Cooling_Pow_Dem_4',
                                 'Zone_1_HC_Action']}
#'Damper_0','Damper_1','Damper_2','Damper_3','Damper_4'
KPI_hist = {key: [] for key in kpi_list}
KPI_hist['episodes'] = []
KPI_hist['scores'] = []
# --------------------

# loading previous memory buffer
if last_ep == 0:
    mem_list_1 = []
else:
    mem_list_1 = pd.read_csv("RL_Data_test/04_Mem/mem_data_" + str(last_ep) + ".csv", dtype=object)
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

print ("Loading Weights")
Agent_1.model_load_weights("RL_Data_test/02_NN/DQN_" + str(last_ep) + ".h5")  # From 2nd episode


print('\n Starting Simulation...')
plotutils = dict(time = [i / 3600 for i in range(0, int(episode_length) + step, step)],
                 lostp = [21 if 6 <= i / 3600 <= 20 else 15.6 for i in range(0, int(episode_length) + step, step)],
                 histp = [24 if 6 <= i / 3600 <= 20 else 26.7 for i in range(0, int(episode_length) + step, step)],
                 length = episode_length)
zonetemp = []
heatingcoil = []
fig, axes = plt.subplots(2, 1, figsize=(10,10))
plt.ion()
plt.show()

# Simulation Loop
for e in range(last_ep,last_ep+episodes):
    Agent_1.model_load_weights("RL_Data_test/02_NN/DQN_" + str(e) + ".h5")  # From 2nd episode
    Agent_1.update_target_model()
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

        # Historian['Damper_0'].append(u['PSZACcontroller_oveDamCor_u'])
        # Historian['Damper_1'].append(u['PSZACcontroller_oveDamP1_u'])
        # Historian['Damper_2'].append(u['PSZACcontroller_oveDamP2_u'])
        # Historian['Damper_3'].append(u['PSZACcontroller_oveDamP3_u'])
        # Historian['Damper_4'].append(u['PSZACcontroller_oveDamP4_u'])
        zonetemp.extend([building_states['senTemRoom1_y'] - 273.15])
        heatingcoil.extend([building_states['senPowPer1_y']])
        plot(zonetemp, heatingcoil, Historian, axes, plotutils)


    # Print KPIs
    kpi = (env.get_KPIs())

    for kpi_name in kpi_list:
        KPI_hist[kpi_name].append(kpi[kpi_name])
    KPI_hist['episodes'].append(e)
    KPI_hist['scores'].append(score)
    print("Agent Memory : {}".format(len(Agent_1.memory)))

    KPI_df = pd.DataFrame.from_dict(KPI_hist)
    KPI_df.to_csv("RL_Data_test/01_KPI/dr_KPI_v2_" + str(e) + ".csv")

    df_m_1 = pd.DataFrame(mem_list_1, columns=['States', 'Action', 'Reward', 'Next_State', 'Done'])
    df_m_1.to_csv("RL_Data_test/04_Mem/mem_data_" + str(e) + ".csv")

    Historian_df = pd.DataFrame.from_dict(Historian)
    Historian_df.to_csv("RL_Data_test/dr_data_test_v2_" + str(e) + ".csv")
    Agent_1.model_save_weights("RL_Data_test/02_NN/DQN_" + str(e) + ".h5")






print('\nTest case complete.')
# --------------------
# Get result data

env.print_KPIs()



