import requests
import numpy as np;import pandas as pd
import gym
from gym import spaces
import collections
from collections import OrderedDict
import math; import random; from statistics import mean
from c5_functions import *
from c6_solar_pv import *
from pathlib import Path
from c7_reward_calc import *
from c8_variables import * 
from c9_RL_functions import * 
import sys,os
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'openai-gym'))
from boptestGymEnv import BoptestGymEnv
import pvlib
from pvlib import pvsystem
from torch.utils.tensorboard import SummaryWriter
from replay_memory import ReplayMemory
import argparse
import datetime
import itertools
import torch
from sac import SAC

updates = 0
parser = argparse.ArgumentParser(description='PyTorch Soft Actor-Critic Args')
parser.add_argument('--env-name', default="HalfCheetah-v2",
                    help='Mujoco Gym environment (default: HalfCheetah-v2)')
parser.add_argument('--policy', default="Gaussian",
                    help='Policy Type: Gaussian | Deterministic (default: Gaussian)')
parser.add_argument('--eval', type=bool, default=True,
                    help='Evaluates a policy a policy every 10 episode (default: True)')
parser.add_argument('--gamma', type=float, default=0.995, metavar='G',
                    help='discount factor for reward (default: 0.99)')
parser.add_argument('--tau', type=float, default=0.0075, metavar='G',
                    help='target smoothing coefficient(τ) (default: 0.005)')
parser.add_argument('--lr', type=float, default=0.0003, metavar='G',
                    help='learning rate (default: 0.0003)')
parser.add_argument('--alpha', type=float, default=0.03, metavar='G',
                    help='Temperature parameter α determines the relative importance of the entropy\
                            term against the reward (default: 0.2)')
parser.add_argument('--automatic_entropy_tuning', type=bool, default=False, metavar='G',
                    help='Automaically adjust α (default: False)')
# parser.add_argument('--seed', type=int, default=123456, metavar='N',
#                     help='random seed (default: 123456)')
parser.add_argument('--batch_size', type=int, default=144*5, metavar='N',
                    help='batch size (default: 256)')
parser.add_argument('--num_steps', type=int, default=1000001, metavar='N',
                    help='maximum number of steps (default: 1000000)')
parser.add_argument('--hidden_size', type=int, default=144*5, metavar='N',
                    help='hidden size (default: 256)')
parser.add_argument('--updates_per_step', type=int, default=10, metavar='N',
                    help='model updates per simulator step (default: 1)')
parser.add_argument('--start_steps', type=int, default=10000, metavar='N',
                    help='Steps sampling random actions (default: 10000)')
parser.add_argument('--target_update_interval', type=int, default=1, metavar='N',
                    help='Value target update per no. of updates per step (default: 1)')
parser.add_argument('--replay_size', type=int, default=1000000, metavar='N',
                    help='size of replay buffer (default: 10000000)')
parser.add_argument('--cuda', action="store_true",
                    help='run on CUDA (default: False)')
args = parser.parse_args()



last_ep =0
episodes = 2
batch_size = args.batch_size
epochs = 10


for episode in range(last_ep+1,last_ep+episodes+1):
     cmd1 = "sudo sysctl vm.drop_caches=1"
     cmd2 = "sudo sysctl vm.drop_caches=2"
     cmd3 = "sudo sysctl vm.drop_caches=3"

     os.system(cmd1)
     os.system(cmd2)
     os.system(cmd3)

     memory = ReplayMemory(args.replay_size)
     training_batch =24

     state_dim = custom_observation_space.shape[0]
     action_dim = custom_action_space.shape[0]
     path = 'RL_Data/01_Normal_run_600_v1/'

    
     score = 0
     agent = SAC(custom_observation_space.shape[0], custom_action_space, args)
     # agent = Agent(action_dim, state_dim,replay_buffer_size=288*400,hidden_dim=[500,800,500],path=path)    
     day_no = np.random.choice(train_days)
     dr_rand_start = random.uniform(14.5,18.0)
     dr_rand_end = dr_rand_start + random.uniform(1.5,3)
     DR_time = [3600 * dr_rand_start, 3600 * dr_rand_end]
     episode_length = 3600*24
     start_time = 24 * 3600 * day_no
     count = 0
     lstm_count = 0      
     total_cost, tot_energy_cost, tot_tdisc_cost, tot_ppen_cost, tot_energy_sold_cost = 0,0,0,0,0
     env = BoptestGymEnv(episode_length=episode_length,
                         Ts=step,
                         testcase='spawnrefsmalloffice',                         
                         start_time=start_time,
                         actions=actions,
                         building_obs=building_obs,
                         forecast_obs=forecast_obs,
                         dr_obs=dr_obs,
                         kpi_zones=kpi_zones,
                         dr_power_limit=50000,  # in watts
                         DR_event=True,
                         DR_time=DR_time,
                         lower_obs_bounds=lower_obs_bounds,
                         upper_obs_bounds=upper_obs_bounds,                        
                         n_obs=True)

     extra_info = init_extra_info()       
     
     # SAC_Agent = Agent(input_dims=custom_observation_space.shape,env_space=custom_action_space,n_actions=custom_action_space.shape[0])
     path_NN = path+'02_NN/'  
     if last_ep>1:
          print ("loading weights and data")
          agent.load_checkpoint(ckpt_path=path_NN+"checkpoints/sac_checkpoint_"+str(last_ep)+"_")    
          

     file_names = os.listdir(path+'04_Mem/')
     print ("file names: {}".format(file_names))
     for file_name in file_names[0:]:
          df = pd.read_pickle(path+"04_Mem/"+str(file_name))
          print ("loading: {}".format(file_name))
          for i in range(len(df)):
               state = df.iloc[i]['states']
               reward = df.iloc[i]['reward']
               action = df.iloc[i]['action']
               next_state = df.iloc[i]['next_states']
               done = df.iloc[i]['done']
               # print ("state:{}".format(state))
               memory.push(state,action,reward,next_state,done)

     print ("check 451")
     

     '''data for episode'''
     df = pd.DataFrame(columns=['states','action','next_states','reward','done'],dtype=np.float64)
     '''data for episode'''

     '''Battery Initialize'''
     cur_soc_n = np.random.uniform(0.1,0.2)
     cur_soc = cur_soc_n* batt_info['batt_cap']
     '''Battery Initialize'''

   
     states_n = env.reset()

     states = np.array(states_n)*(upper_obs_bounds-lower_obs_bounds) + lower_obs_bounds
     building_states = env.get_building_states()     
     mean_temp_n = (states_n[0]+states_n[1]+states_n[2]+states_n[3]+states_n[4])/5
     agent_state_n = np.array([mean_temp_n, states_n[5],states_n[6],states_n[7],states_n[8],states_n[9],states_n[10],states_n[11],cur_soc_n])

     print ("Last episode: {}".format(last_ep))
     last_ep = episode         
   

     for i in range(int(episode_length/step)):  
          print ("Episode: {}, i: {}; DR: {}".format(episode,i,[dr_rand_start,dr_rand_end]))       
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
          '''Get Building and weather Data'''  


          '''Agent Related'''
          mean_temp_n = (states_n[0] + states_n[1] + states_n[2] + states_n[3] + states_n[4])/5
          curr_agent_states_n = np.array([[mean_temp_n,states_n[5],states_n[6],states_n[7],states_n[8],states_n[9],states_n[10],states_n[11],cur_soc_n]])
          
          
          if i%2==0:
               curr_agent_states_n_600 = curr_agent_states_n

               if len(memory)<batch_size:
                    unprocessed_act = custom_action_space.sample()
               else:
                    unprocessed_act = agent.select_action(state=curr_agent_states_n[0].tolist())      

               if cur_soc==0 and unprocessed_act[1]<0:
                    # unprocessed_act = [unprocessed_act[0],0]
                    r_mod = 200*unprocessed_act[1] # reward penalty to discourage the agent to discharge when state of charge of battery is already at zero 
               else:
                    r_mod = 0 


          processed_action,act_01,act_02 = action_sac_proc_v3(unprocessed_action=unprocessed_act)         
          '''Agent Related'''            


          '''Advance Simulation'''
          next_states_n,_, done, info = env.step(processed_action)    
          '''Advance Simulation'''



          ''' PV Lib '''
          print ("PV inputs, temp_air: {}; dni: {}; dhi: {}; ghi: {}; wsp: {}".format(temp_air,dni,dhi,ghi,w_sp))
          if hours<5 or hours>18.5:
               ac_power = 0 
          else:                       
               # ac_power = get_total_pv(temp_air=temp_air,dni=dni,dhi=dhi,ghi=ghi,w_sp=w_sp)  
               ac_power =get_total_pv_precal(day_no,i)        
          dc_power = ac_power*0.95          
          ''' PV Lib '''

          '''kpi related'''
          individual_rewards = env.get_individual_rewards()               
          '''kpi related'''


          ''' Battery Calculation  '''
          plug_power = calc_plug_power(day_no=day_no,sen_hou=hours,step=step)
          tot_hvac_power = building_states['senPowCor_y'] + building_states['senPowPer1_y'] + building_states['senPowPer2_y'] + \
                    building_states['senPowPer3_y'] + building_states['senPowPer4_y'] 
          tot_power = tot_hvac_power + plug_power
          
          cur_soc,batt_pow_prov,net_grid_power,pow_sold,other_info = battery_calc(act_02=act_02,                                                         
                                                         batt_info = batt_info,
                                                         cur_soc= cur_soc,
                                                         step=step,
                                                         tot_pow=tot_power,
                                                         dc_power=dc_power)   

          print ()
          print ("Whole building demand: {}; Net Building power: {}".format(tot_power,net_grid_power))
          print ("Batt_pow_prov: {}; Power Sold: {}; PV power: {}".format(batt_pow_prov,pow_sold,dc_power))                  
          print ("SOC: {}".format(cur_soc))
          print ()

          net_grid_energy = net_grid_power*step/3600   
          # print ("Net grid energy: {}".format(net_grid_energy))
          ''' Battery Calculation '''                    
          
          print ("Zone Core: {}, Zone 1: {}, Zone 2: {}, Zone 3: {}, Zone 4: {}".format(building_states['senPowCor_y'],building_states['senPowPer1_y'],building_states['senPowPer2_y'],building_states['senPowPer3_y'],building_states['senPowPer4_y']))

          '''Main States Pre-processing'''          
          cur_soc_n = cur_soc/batt_info['batt_cap']   
          building_states = env.get_building_states()          
          next_mean_temp = (building_states['senTemRoom_y']+building_states['senTemRoom1_y'] +building_states['senTemRoom2_y'] +building_states['senTemRoom3_y']+building_states['senTemRoom4_y'])/5
          next_mean_temp_n = (next_states_n[0]+next_states_n[1]+next_states_n[2]+next_states_n[3]+next_states_n[4])/5
          next_agent_states_n = np.array([[next_mean_temp_n,next_states_n[5],next_states_n[6],next_states_n[7],next_states_n[8],next_states_n[9],next_states_n[10],next_states_n[11],cur_soc_n]])
          next_agent_states= convert_to_state(agent_state_n=next_agent_states_n,lower_bnds=agent_lower_obs_bounds,upper_bnds=agent_upper_obs_bounds)
          building_states = env.get_building_states()
          '''Main States Pre-processing''' 
     
          print ("next_state_n: {}".format(next_agent_states))
          


          '''extra info and reward calc'''       
          extra_info['price'].append(price)
          extra_info['net_grid_energy'].append(net_grid_energy)
          extra_info['plug_power'].append(plug_power)
          extra_info['net_grid_power'].append(net_grid_power)          
          extra_info['tot_building_power'].append(tot_power)
          extra_info['score'].append(score)   
          extra_info['cur_soc'].append(cur_soc) 
          extra_info['pow_sold'].append(pow_sold) 
          extra_info['act_01'].append(act_01) 
          extra_info['act_02'].append(act_02)           
          extra_info['pv_pow'].append(dc_power)           
          extra_info['batt_pow_prov'].append(batt_pow_prov) 
          # extra_info['other_info'].append(other_info)           
               

          reward,cost,energy_cost,tdisc_cost,ppen_cost,energy_sold_cost,mod_reward,single_reward= calc_reward_function(sen_hou=next_agent_states[0][1],
                                                                                                    DR_time = DR_time,
                                                                                                    next_temp =np.array([next_agent_states[0][0]]),
                                                                                                    individual_rewards= individual_rewards,                                                                                                   
                                                                                                    extra_info=extra_info,
                                                                                                    i=i
                                                                                                    )
          reward = reward+r_mod
          print ("mod reward: {}".format(mod_reward))    
          print ("single reward: {}".format(single_reward))        
          extra_info['mod_reward'].append(reward)  
          extra_info['r_tdisc'].append(mod_reward['r_tdisc']) 
          extra_info['r_energy'].append(mod_reward['r_energy']) 
          extra_info['r_ppen'].append(mod_reward['r_ppen']) 
          extra_info['r_energy_sold'].append(mod_reward['r_energy_sold']) 
          extra_info['cost_tdisc'].append(single_reward['cost_tdisc']) 
          extra_info['cost_energy'].append(single_reward['cost_energy']) 
          extra_info['cost_ppen'].append(single_reward['cost_ppen']) 
          extra_info['cost_energy_sold'].append(single_reward['cost_energy_sold']) 

          

          '''extra info and reward calc''' 
          

          # print ("extra info after reward calc: {}".format(extra_info))   

          print ("curr_agent_state_n: {}".format(curr_agent_states_n))
          print ("next_agent_state:_n {}".format(next_agent_states_n)) 


          if (i+1)%2==0:
               memory.push(curr_agent_states_n[0], unprocessed_act, reward, next_agent_states_n[0],done) # Append transition to memory
               # agent.remember(curr_agent_states_n[0].tolist(),unprocessed_act,reward,next_agent_states_n[0].tolist(),done)
               df1 = pd.DataFrame({'states':[curr_agent_states_n[0]],'action':[unprocessed_act],'next_states':[next_agent_states_n[0]],'reward':[reward],'done':[done]})
               df = pd.concat([df, df1])
          # print (df.tail())         

          curr_agent_states_n = next_agent_states_n 
          states_n = next_states_n 

          total_cost += cost
          tot_energy_cost += energy_cost
          tot_tdisc_cost  +=  tdisc_cost 
          tot_ppen_cost += ppen_cost
          tot_energy_sold_cost += energy_sold_cost
          score += reward
          '''Agent Related'''              


          '''Training Models'''
          
          
          if (count%training_batch)==0:  
               print ("check 1, memory: {}".format(len(memory)))                    
               if len(memory)> batch_size:      
                    for e in range(epochs):             
                         critic_1_loss, critic_2_loss, policy_loss, ent_loss, alpha = agent.update_parameters(memory, args.batch_size, updates)
                         updates += 1
                         print ("eposhcs: {}".format(e))
                         print ("q_value loss1: {}".format(critic_1_loss))
                         print ("q_value loss2: {}".format(critic_2_loss))
                         print ("policy loss: {}".format(policy_loss))
                         # print ("ent loss: {}".format(ent_loss))   
                         # print ("alpha: {}".format(alpha))   
                         print ()   
               # agent_search.train_lstm(training_epochs=50)     
          '''Training Models'''   

          print ("total cost: {}".format(total_cost))  
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
               KPI_hist['energy_sold_total_cost'].append(tot_energy_sold_cost)
               KPI_hist['ppen_total_cost'].append(tot_ppen_cost)
               KPI_hist['DR_start_time'].append(dr_rand_start)
               KPI_hist['DR_end_time'].append(dr_rand_end)
               KPI_hist['DR_duration'].append(dr_rand_end-dr_rand_start)     

               KPI_df = pd.DataFrame.from_dict(KPI_hist)
               KPI_df.to_csv(path+"01_KPI/KPI_" + str(episode) + "_SAC.csv")     
               agent.save_checkpoint(env_name=episode,
                                     ckpt_path=path_NN+"checkpoints/sac_checkpoint_"+str(episode)+"_")
               
               df.to_pickle(path+"04_Mem/mem"+str(episode)+".pkl")
                

               
               print ()
               print ()

               env.print_KPIs()
               env.save_episode(filename = path+"03_Data/data_"+str(episode)+".csv",extra_info=extra_info)
               last_ep = episode 
               # env.plot_episode(path+"05_Plot/plot_"+str(episode)+".jpg", [0, 1, 2, 3, 4,'tot'])

        

        

        


