"""
This module manages the simulation of SOM3 in BOPTEST. It initializes,
steps and computes controls for the HVAC system.
The testcase docker container must be running before launching this
script.
"""

# GENERAL PACKAGE IMPORT
# ----------------------
import requests
import numpy as np;import pandas as pd
import gym
from gym import spaces
import collections
from collections import OrderedDict
import math; import random; from statistics import mean

from RL_functions import *
from d6_functions import *
from pathlib import Path
from DQN_Agent_IRL import DQN_Agent
from d8_q_transfer_functions import get_q_value

import sys
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent.parent / 'interfaces' / 'openai-gym'))
from boptestGymEnv import BoptestGymEnv


path = 'RL_Data/03_DQN_IRL/'
reward_maxent = np.load('RL_Data/00_Tables/final_reward_maxent.npy')

'''KPI Initializer'''
kpi_list = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']
KPI_hist = {key: [] for key in kpi_list}
KPI_hist['episodes'] = []; KPI_hist['scores'] = []
KPI_hist['total_cost'] = []; KPI_hist['energy_total_cost'] = []; KPI_hist['tdisc_total_cost'] = []
KPI_hist['day_no'] = []; KPI_hist['DR_start_time'] = []; KPI_hist['DR_end_time'] = []
'''KPI Initializer'''

# ----------------------
# TEST CONTROLLER IMPORT

'''ACTB Initialize'''
step = 300
actions = ['PSZACcontroller_oveCooPer1_u','PSZACcontroller_oveCooPer2_u',
           'PSZACcontroller_oveCooPer3_u','PSZACcontroller_oveCooPer4_u',
           'PSZACcontroller_oveCooCor_u','PSZACcontroller_oveDamCor_u','PSZACcontroller_oveDamP1_u',
           'PSZACcontroller_oveDamP2_u','PSZACcontroller_oveDamP3_u','PSZACcontroller_oveDamP4_u',
           "PSZACcontroller_oveHeaStpCor_u","PSZACcontroller_oveHeaStpPer1_u","PSZACcontroller_oveHeaStpPer2_u","PSZACcontroller_oveHeaStpPer3_u","PSZACcontroller_oveHeaStpPer4_u"]


kpi_zones = ["0","1","2","3","4"]
building_obs = ['senTemRoom_y','senTemRoom1_y','senTemRoom2_y','senTemRoom3_y','senTemRoom4_y','senHouDec_y']
forecast_obs = {'TDryBul': [0]}

test = False


dr_obs = [-1,0]
min_oa, max_oa = 15,35

min_temp, max_temp = 273.15+16, 273.15+33
lower_obs_bounds = [min_temp,min_temp,min_temp,min_temp,min_temp,0,min_oa, 0, 0]
upper_obs_bounds = [max_temp,max_temp,max_temp,max_temp,max_temp,24,max_oa,1, 1]
index = [i for i in range(len(lower_obs_bounds))]
score_list = list()

if test==True:
    last_ep= 0 
else:
    last_ep = 100

starting_temp = 18
episodes = 1



if test==True:
    dr_start_times = [17.497,16.553,17.140,17.322,16.775,17.072,17.259]
    dr_end_times = [19.525,18.959,20.074,19.465,19.208,19.509,19.643]
    test_days = [213,215,247,233,248,185,153]
    episodes = len(test_days)

price = {'energy': 0.0984, 't_disc': 0.8, 'dr_price': 7.89 }
extra_info_lstm = dict()

# extra_info['price'] = price
'''ACTB Initiliaze'''
print('\nRunning controller script...')


for episode in range(last_ep+1,last_ep+episodes+1):    
    score = 0
    prev_sp_list = [273.15+starting_temp,273.15+starting_temp,273.15+starting_temp,273.15+starting_temp,273.15+starting_temp]
    curr_sp_list = prev_sp_list
    day_no = np.random.choice([141,149,156,158,159,164,165,166,169,170,171,176,177,178,184,186,188,192,193,198,199,200,204,206,207,208,209,212,214,216,221,232,240,246,253])
    dr_rand_start = random.uniform(16.5,17.5)
    dr_rand_end = dr_rand_start + random.uniform(2,3)
    if test==True:
        day_no = test_days[episode-1]
        dr_rand_start = dr_start_times[episode-1]
        dr_rand_end = dr_end_times[episode-1]
    DR_time = [3600 * dr_rand_start, 3600 * dr_rand_end]
    episode_length = 3600 * 24
    start_time = 24 * 3600 * day_no
    count = 0    
    total_cost, tot_energy_cost, tot_tdisc_cost, tot_ppen_cost = 0,0,0,0
    env = BoptestGymEnv(episode_length=episode_length,
                        Ts=step,
                        testcase='spawnrefsmalloffice',
                        start_time=start_time,
                        actions=actions,
                        building_obs=building_obs,
                        forecast_obs=forecast_obs,
                        dr_obs=dr_obs,
                        kpi_zones=kpi_zones,
                        dr_power_limit=9000,  # in watts
                        DR_event=True,
                        DR_time=DR_time,
                        lower_obs_bounds=lower_obs_bounds,
                        upper_obs_bounds=upper_obs_bounds,                        
                        n_obs=True)


    c=0.95**(last_ep)
    extra_info = dict()
    extra_info['s0'] = []
    extra_info['s1'] = []
    extra_info['s2'] = []
    extra_info['s3'] = []
    
    # extra_info['tot_power'] = []
    extra_info['plug_power'] = []
    extra_info['hvac_power'] = []
    extra_info['reward_irl'] = []
    extra_info['reward_dqn'] = []
    extra_info['curr_agent_states_n'] = []
    

    '''States'''
     
    # 01 - Mean Temperature
    # 02 - Time in Hours (state_n[5])
    # 03 - OA Temmperature (state_n[6])
    # 04 - DR signal 
    
    '''States'''    
    counter = 0
    agent_state_size = 5 #env.observation_space.shape
    env.set_DR_time(DR_time)
    state_n = env.reset()
    building_states = env.get_building_states()
    forecasts = env.get_forecast()   
    hours = building_states['senHouDec_y']         
    oa_air = forecasts['TDryBul'][0]  

    print ("agent state size: {}".format(agent_state_size))

    print ("OA Air Temp: {}".format(oa_air))
    sp = get_sp(hours)[0]   
    
    mean_T = (building_states['senTemRoom_y']+building_states['senTemRoom1_y'] +building_states['senTemRoom2_y'] +building_states['senTemRoom3_y']+building_states['senTemRoom4_y'])/5
    mean_T_n = (state_n[0]+state_n[1]+state_n[2]+state_n[3]+state_n[4])/5

    dr_m1 = state_n[7]*18
    dr_m0 = state_n[8]    

    dr_index = get_dr_index_2(dr_m1=dr_m1,dr_0=dr_m0,hour_dec=hours)
    T_index = get_temp_index(temp=mean_T)
    hr_index = get_occ_signal(time=state_n[5]*24)
    oa_index = get_oa_index(oa=oa_air)    

    curr_index_states = np.array([[T_index,hr_index,oa_index,dr_index]])    
    curr_agent_states_n = np.array([[mean_T_n,state_n[5],state_n[6],state_n[7],state_n[8]]])  

    Agent_1 = DQN_Agent(agent_state_size, 2)

    if last_ep == 0:
        mem_list_1 = []
        Agent_1.model_load_weights(path+"02_NN/DQN_" + str(last_ep) + ".h5")
    else:
        Agent_1.model_load_weights(path+"02_NN/DQN_" + str(last_ep) + ".h5")  # From 2nd episode
        mem_list_1 = mem_processor(filename="RL_Data/02_DQN/04_Mem/mem_data_" + str(last_ep) + ".csv")
        for i in range(len(mem_list_1)):
            state_m1 = mem_list_1.iloc[i][0]; action_m1 = mem_list_1.iloc[i][1]
            reward_m1 = mem_list_1.iloc[i][2]; next_state_m1 = mem_list_1.iloc[i][3];
            done_m1 = mem_list_1.iloc[i][4]
            Agent_1.append_sample(state_m1, action_m1, reward_m1, next_state_m1, done_m1)
    
    c=0.95**(last_ep)
    

    print("Modified State")

    for i in range(int(episode_length/step)):           
        sp = get_sp(hours)[0]
        abs_time = i * step             
        minutes = ((abs_time) % 3600) / 60
        days = math.floor(abs_time / (3600 * 24))
        hours = building_states['senHouDec_y'] 
        counter= counter + 1       
        occupancy = get_occupancy(hours)  

        ''' print statements - before step '''
        print("Episode: {}".format(episode))        
        print(' Day no: {}, Hours: {}, i {}, Count: {}'.format(day_no, hours, i, counter))
        print("DR Start and End : {}".format([dr_rand_start,dr_rand_end]))    
        print("Total Occupancy : {}".format(occupancy)) 
        ''' print statements - before step ''' 

        if oa_air<19:
            dif = (19-oa_air)
            if dif<1:
                dif =2
            else:
                s =  dif*2
        else:
            s=1

        if (hours >= (np.array(DR_time)/3600)[0]) & (hours< (np.array(DR_time)/3600)[1]):
            # print("First Condition")            
            dr_power_limit = 9000 
            w = [-50, -1, -1] 
            env.change_dr_limit(dr_power_limit)          
        else:
            # print("Second Condition")            
            dr_power_limit = 30000
            w = [-50*s, -1, 0]  
            env.change_dr_limit(dr_power_limit) 


        print ("current agent state: {}".format(curr_agent_states_n))

        act = Agent_1.get_action(curr_agent_states_n)

        s0 = get_index(s=curr_index_states[0])
        act_q = get_q_value(state=s0)

        # if random.uniform(0,1)>0.9:
        #     act = np.argmax(act_q)
        # else:
        #     pass

        q_1 = Agent_1.target_predict_qvalue(state = curr_agent_states_n)

        if test==False:
            if counter % (12*2) == 0:
                Agent_1.train_model()

            if counter % (12 *6) == 0:
                Agent_1.update_target_model()         
              

        KPI_rewards = {
        "ener_tot": {"hyper": price['energy'] * w[0], "power": 1},
        "tdis_tot": {"hyper": price['t_disc'] * w[1] * occupancy, "power": 1},
        "idis_tot": {"hyper": 0, "power": 1},
        "cost_tot": {"hyper": 0, "power": 1},
        "emis_tot": {"hyper": 0, "power": 1},
        "power_pen":{"hyper": price['dr_price'] * w[2], "power": 1} }      

        env.change_rewards_weights(KPI_rewards=KPI_rewards) 


        '''Get Building Data'''                
        
        
        building_states = env.get_building_states()
        forecasts = env.get_forecast()      

        dr_m1 = state_n[7]*18
        dr_m0 = state_n[8]
        oa_air = forecasts['TDryBul'][0]       
           
                       
        # index_curr_states = np.array([T_index,hr_index,oa_index,dr_index,state_n[8]]) 
        mean_temp_n = (state_n[0] + state_n[1] + state_n[2] + state_n[3] + state_n[4])/5
        # agent_state_n = np.array([mean_temp_n,state_n[5],state_n[6],state_n[7],state_n[8],state_n[9],state_n[10],state_n[11],cur_soc_n])
        '''Get Building Data'''   
        
        
        '''Agent Related'''            
        flow_zi = 0.15        
        flow_rate = [flow_zi,flow_zi,flow_zi,flow_zi,flow_zi]
        curr_act_list = [act,act,act,act,act]      
        ht_stp = [273.15+15,273.15+15,273.15+15,273.15+15,273.15+15]     
        processed_action = [*curr_act_list,*flow_rate,*ht_stp]     
                        
        '''Agent Related'''                 

                

        '''Advance Simulation'''
        next_state_n,_, done, info = env.step(processed_action)    
        '''Advance Simulation''' 

        ''' Form next states'''
        next_mean_T_n = (next_state_n[0] + next_state_n[1] + next_state_n[2] + next_state_n[3] + next_state_n[4])/5
        next_agent_states_n = np.array([[next_mean_T_n, next_state_n[5],next_state_n[6],next_state_n[7],next_state_n[8]]])  

        building_states = env.get_building_states()
        next_mean_T = (building_states['senTemRoom_y']+building_states['senTemRoom1_y'] +building_states['senTemRoom2_y'] +building_states['senTemRoom3_y']+building_states['senTemRoom4_y'])/5
        forecasts = env.get_forecast()               
        next_oa_air = forecasts['TDryBul'][0] 
        next_dr_m1 = next_state_n[7]*18
        next_dr_m0 = next_state_n[8]       


        next_T_index = get_temp_index(temp=next_mean_T-273.15)
        next_hr_index = get_occ_signal(time=next_state_n[5]*24)
        next_oa_index = get_oa_index(oa=next_oa_air)   
        next_dr_index = get_dr_index_2(dr_m1=next_dr_m1,dr_0=next_dr_m0,hour_dec=hours)

        next_index_states = np.array([[next_T_index,next_hr_index,next_oa_index,next_dr_index]])   

        irl_state = get_index(s=next_index_states[0]) # get state id 
        reward_irl =  reward_maxent[irl_state]   

        ''' Form next states'''


        '''kpi related'''

        individual_rewards = env.get_individual_rewards()
        plug_power = calc_plug_power(day_no=day_no,sen_hou=hours,step=step)

        tot_hvac_pow = building_states['senPowCor_y'] + building_states['senPowPer1_y'] + building_states['senPowPer2_y'] + \
                building_states['senPowPer3_y'] + building_states['senPowPer4_y'] 

        energy_cost =  price['energy'] * individual_rewards['Energy']
        tdisc_cost = price['t_disc'] * individual_rewards['Thermal_Discomfort'] * occupancy 
        ppen_cost = price['dr_price'] * individual_rewards['Power_Penalty']

        tot_energy_cost += energy_cost 
        tot_tdisc_cost  +=  tdisc_cost
        tot_ppen_cost += ppen_cost

        cost = price['energy'] * individual_rewards['Energy'] + price['t_disc'] * individual_rewards[
            'Thermal_Discomfort'] * occupancy + price['dr_price'] * individual_rewards['Power_Penalty']

        reward_dqn =  w[0]*energy_cost + w[1]*tdisc_cost+ w[2]*ppen_cost

        

        # Modified reward function - adding kpi rewards plus the artificial rewards - with c controlling the importance of the artificial weights 
        reward = reward_dqn+ c*reward_irl


        total_cost += cost
        tot_power = tot_hvac_pow + plug_power 

        print ("agent state: {}".format(curr_agent_states_n))
        print ("indeex state: {}".format(curr_index_states))
        print ("q_value: {}".format(q_1))
        print ("q_value irl: {}, c: {}".format(act_q,c))
        print ("reward_irl: {}, reward_dqn: {}".format(reward_irl,reward_dqn))        
        print ("Action taken: {}, final rewards: {}".format(act,reward))
        print("Exploration {}".format(Agent_1.exploration_value()))
        print("Score {}".format(score))
        print("\n")

        Agent_1.append_sample(curr_agent_states_n,act, reward, next_agent_states_n, done)

        if test==False:
            if last_ep == 0:
                mem_list_1.append((curr_agent_states_n, act, reward,next_agent_states_n, done))  # 1st episode
            else:
                mem_list_1 = mem_list_1.append({'States': curr_agent_states_n, 'Action': act, 'Reward': reward, 'Next_State': next_agent_states_n, 'Done': done},
                    ignore_index=True)

        score += reward_dqn
        print ("Agent Memory: {}".format(len(Agent_1.get_memory())))

        '''kpi related'''     
              

        '''Agent Related'''

        ''' print statements - after step '''
        print("Individual Rewards")
        print(individual_rewards)
        print ()
        print ("Full Action U-Vector :{}".format(processed_action))    
        print("Total Power;  Zone 0:{}, Zone 1:{}, Zone 2: {}, Zone 3: {}, Zone 4; {}".format(
            round(building_states['senPowCor_y'], 2),
            round(building_states['senPowPer1_y'], 2),
            round(building_states['senPowPer2_y'], 2),
            round(building_states['senPowPer3_y'], 2),
            round(building_states['senPowPer4_y'], 2)))        
        print ("Next State, Reward, Done, Info: ")
        
        print(next_agent_states_n,reward, done, info)
        print()
        print("Total Power of all Zones: {}".format(tot_hvac_pow))
        print("Room Temperature;  Zone 0: {}, Zone 1: {}, Zone 2: {}, Zone 3: {}, Zone 4: {}, Mean Temp: {}".format(
            building_states['senTemRoom_y'],
            building_states['senTemRoom1_y'],
            building_states['senTemRoom2_y'],
            building_states['senTemRoom3_y'],
            building_states['senTemRoom4_y'],next_mean_T_n*(max_temp-min_temp)+min_temp))
        print ()
        print("Score: {}".format(score))
        print ("Total Cost: {}, Cost:  {}".format(total_cost,cost))        
        ''' print statements - after step '''

        print ("curr index states: {}".format(curr_index_states))
        

        ''' Extra info storage'''
                 
        extra_info['s0'].append(curr_index_states[0][0])
        extra_info['s1'].append(curr_index_states[0][1])
        extra_info['s2'].append(curr_index_states[0][2])
        extra_info['s3'].append(curr_index_states[0][3])        
        extra_info['plug_power'].append(plug_power)
        extra_info['hvac_power'].append(tot_hvac_pow)
        extra_info['reward_irl'].append(reward_irl)
        extra_info['reward_dqn'].append(reward_dqn)
        extra_info['curr_agent_states_n'].append(curr_agent_states_n)
        
        ''' Extra info storage'''  

        # print (extra_info)

        ''' Form current states'''
        curr_agent_states_n = next_agent_states_n  
        curr_index_states = next_index_states  
        ''' Form current states'''              
                
        
        print ()
        print ()
        print("\n")

        
        if done:
            # Print KPIs
            kpi = (env.get_KPIs())
            score_list.append(score)

            for kpi_name in kpi_list:
                KPI_hist[kpi_name].append(kpi[kpi_name])
            KPI_hist['episodes'].append(episode)
            KPI_hist['scores'].append(score)
            KPI_hist['total_cost'].append(total_cost)
            KPI_hist['day_no'].append(day_no)
            KPI_hist['energy_total_cost'].append(tot_energy_cost)
            KPI_hist['tdisc_total_cost'].append(tot_tdisc_cost)
            KPI_hist['DR_start_time'].append(dr_rand_start)             
            KPI_hist['DR_end_time'].append(dr_rand_end)

            # print (KPI_hist)
            KPI_df = pd.DataFrame.from_dict(KPI_hist)

            
            KPI_df.to_csv(path+"01_KPI/KPI_" + str(episode) + "_dqn_irl.csv")         
            episode_path  = path+"03_Data/data_"+str(episode)+"_"+str(day_no)+".csv"

            if test==False:
                df_m_1 = pd.DataFrame(mem_list_1, columns=['States', 'Action', 'Reward', 'Next_State', 'Done'])
                df_m_1.to_csv(path+"04_Mem/mem_data_" + str(episode) + ".csv")

            Agent_1.model_save_weights(path+"02_NN/DQN_" + str(episode) + ".h5")

            print ("episode path: {}".format(episode_path))
            env.print_KPIs()
            env.save_episode(episode_path,extra_info)
            env.plot_episode(path+"05_Plot/plot_"+str(episode)+".jpg", [0, 1, 2, 3, 4,'tot'])

            state_n, done, score, SAVING = env.reset(), False, 0, ''
            mean_temp_n = (state_n[0] + state_n[1] + state_n[2] + state_n[3] + state_n[4])/5
            last_ep = episode

            # Print KPIs


print('\nTest case complete.')
# -------------



