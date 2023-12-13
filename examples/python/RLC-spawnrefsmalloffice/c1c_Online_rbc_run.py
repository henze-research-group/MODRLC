import requests
import numpy as np;import pandas as pd
import gym
from gym import spaces
import collections
from collections import OrderedDict
import math; import random; from statistics import mean
from c5_functions import *
from c6_solar_pv import *
from c2_LSTM_model import LSTM_Model
from pathlib import Path
from c7_reward_calc import *
from c8_variables import * 
from c9_RL_functions import * 
import sys
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'openai-gym'))
from boptestGymEnv import BoptestGymEnv
import pvlib
from pvlib import pvsystem

path = 'RL_Data/03_RBC_run/'
last_ep =0 
episodes = len(test_days)

for episode in range(last_ep+1,last_ep+episodes+1):
     score = 0
     prev_sp_list = [273.15+starting_temp,273.15+starting_temp,273.15+starting_temp,273.15+starting_temp,273.15+starting_temp]
     curr_sp_list = prev_sp_list
     day_no = np.random.choice(train_days)
     dr_rand_start = random.uniform(14,16)
     dr_rand_end = dr_rand_start + random.uniform(2.0,3)
     DR_time = [3600 * dr_rand_start, 3600 * dr_rand_end]
     episode_length = 3600*24
     start_time = 24 * 3600 * day_no
     count = 0
     lstm_count = 0      
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

     extra_info = init_extra_info()        
     

     
     '''Battery Initialize'''
     cur_soc_n = np.random.uniform(0.1,0.2)
     cur_soc = cur_soc_n* batt_cap
     '''Battery Initialize'''

     
     state_n = env.reset()

     state = np.array(state_n)*(upper_obs_bounds-lower_obs_bounds) + lower_obs_bounds
     building_states = env.get_building_states()
     hours = building_states['senHouDec_y']
     mean_temp_n = (state_n[0]+state_n[1]+state_n[2]+state_n[3]+state_n[4])/5
     agent_state_n = np.array([mean_temp_n, state_n[5],state_n[6],state_n[7],state_n[8],state_n[9],state_n[10],state_n[11],cur_soc_n])

     print ("Last episode: {}".format(last_ep))
     last_ep = episode
     actor_name,critic1_name,critic2_name,value_name,target_value_name = sac_path_storenames(ep=episode)
     

     for i in range(int(episode_length/step)):  
          print ("Episode: {}, i: {}".format(episode,i))         
          sp = get_sp(hours)[0]
          abs_time = i * step             
          minutes = ((abs_time) % 3600) / 60
          days = math.floor(abs_time / (3600 * 24))
          hours = building_states['senHouDec_y']               
          count += 1   

          print ("hours: {}".format(hours))          
          
          '''Get Building and weather Data'''                
          building_states = env.get_building_states()
          forecasts = env.get_forecast()            
          mean_temp,temp_air,dni,dhi,ghi,w_sp = get_building_weather_data(building_states,forecasts)
          '''Get Building Data'''  


          '''Agent Related'''
          mean_temp_n = (state_n[0] + state_n[1] + state_n[2] + state_n[3] + state_n[4])/5
          agent_state_n = np.array([mean_temp_n,state_n[5],state_n[6],state_n[7],state_n[8],state_n[9],state_n[10],state_n[11],cur_soc_n])
          processed_action,act_01,act_02 = rbc_action_online(hours=hours,DR_time=DR_time,sp=sp) 
          '''Agent Related'''            

          '''Advance Simulation'''
          next_state_n,_, done, info = env.step(processed_action)    
          '''Advance Simulation'''

          ''' PV Lib '''
          ac_power = get_pv_output(temp_air=temp_air,dni=dni,dhi=dhi,ghi=ghi,w_sp=w_sp)         
          dc_power = ac_power*0.95
          ''' PV Lib '''


          ''' Battery Calculation  '''
          # plug_power = calc_plug_power(day_no=day_no,sen_hou=hours,step=step)
          tot_power = building_states['senPowCor_y'] + building_states['senPowPer1_y'] + building_states['senPowPer2_y'] + \
                    building_states['senPowPer3_y'] + building_states['senPowPer4_y'] 

          
          cur_soc,batt_pow_prov,net_grid_power,pow_sold,other_info = battery_calc(act_02=act_02,                                                         
                                                         batt_info = batt_info,
                                                         cur_soc= cur_soc,
                                                         step=step,
                                                         tot_pow=tot_power,
                                                         dc_power=dc_power)   

          print ("SOC: {}".format(cur_soc))

          net_grid_energy = net_grid_power*step/3600   
          ''' Battery Calculation '''  

                  
          '''kpi related'''
          individual_rewards = env.get_individual_rewards()        
          '''kpi related'''

          print ("Zone Core: {}, Zone 1: {}, Zone 2: {}, Zone 3: {}, Zone 4: {}".format(building_states['senPowCor_y'],building_states['senPowPer1_y'],building_states['senPowPer2_y'],building_states['senPowPer3_y'],building_states['senPowPer4_y']))


          '''Agent Related'''          
          cur_soc_n = cur_soc/batt_cap             
          next_mean_T = (building_states['senTemRoom_y']+building_states['senTemRoom1_y'] +building_states['senTemRoom2_y'] +building_states['senTemRoom3_y']+building_states['senTemRoom4_y'])/5
          next_mean_T_n = (next_state_n[0]+next_state_n[1]+next_state_n[2]+next_state_n[3]+next_state_n[4])/5
          next_agent_state_n = np.array([next_mean_T_n,next_state_n[5],next_state_n[6],next_state_n[7],next_state_n[8],next_state_n[9],next_state_n[10],next_state_n[11],cur_soc_n])
          next_agent_state = convert_to_state(agent_state_n=next_agent_state_n,lower_bnds=agent_lower_obs_bounds,upper_bnds=agent_upper_obs_bounds)
          building_states = env.get_building_states()
     
          print ("next_state_n: {}".format(next_state_n))
          # print ("next_agent_state_n: {}".format(next_agent_state_n))
          print ("next_agent_state: {}".format(next_agent_state))          

          extra_info['price'].append(price)
          extra_info['net_grid_energy'].append(net_grid_energy)
          extra_info['net_grid_power'].append(net_grid_power)          
          extra_info['tot_building_power'].append(tot_power)
          extra_info['score'].append(score)   
          extra_info['cur_soc'].append(cur_soc) 
               

          reward,cost,energy_cost,tdisc_cost,ppen_cost,mod_reward = calc_reward_function(sen_hou=next_agent_state[1],
                                                                                                    DR_time = DR_time,
                                                                                                    next_temp =np.array([next_agent_state[0]]),
                                                                                                    individual_rewards= individual_rewards,                                                                                                   
                                                                                                    extra_info=extra_info
                                                                                                    )

          
          print ("mod reward: {}".format(mod_reward))  
          
          extra_info['mod_reward'].append(reward)  
          extra_info['r_tdisc'].append(mod_reward['r_tdisc']) 
          extra_info['r_energy'].append(mod_reward['r_energy']) 
          extra_info['r_ppen'].append(mod_reward['r_ppen']) 
          # extra_info['r_curtpv'].append(mod_reward['r_curtpv']) 
          extra_info['act_01'].append(act_01) 
          extra_info['act_02'].append(act_02)           
          extra_info['pv_pow'].append(dc_power) 
          extra_info['pow_sold'].append(pow_sold) 
          extra_info['batt_pow_prov'].append(batt_pow_prov) 
          extra_info['other_info'].append(other_info) 

          # print ("extra info after reward calc: {}".format(extra_info))   

          agent_state_n = next_agent_state_n 
          state_n = next_state_n 

          total_cost += cost
          tot_energy_cost += energy_cost
          tot_tdisc_cost  +=  tdisc_cost 
          tot_ppen_cost += ppen_cost
          # tot_curt_cost += curt_cost
          score += reward
          '''Agent Related'''          



          # print ("extra info: {}".format(extra_info))  
          print ()
          print ()
          print ()     

          if done:                
               kpi = (env.get_KPIs())
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
               KPI_hist['DR_duration'].append(dr_rand_end-dr_rand_start)     

               KPI_df = pd.DataFrame.from_dict(KPI_hist)
               KPI_df.to_csv(path+"01_KPI/KPI_" + str(episode) + ".csv")              
                           
                             
               print ()
               print ()

               env.print_KPIs()
               env.save_episode(filename = path+"03_Data/data_"+str(episode)+".csv",extra_info=extra_info)
               env.plot_episode(path+"05_Plot/plot_"+str(episode)+".jpg", [0, 1, 2, 3, 4,'tot'])

        

        

        


