
import requests
import numpy as np;import pandas as pd
import gym
from gym import spaces
import collections
from collections import OrderedDict
import math; import random; from statistics import mean
from c3d_SAC import Agent
from sac_2 import SAC
from c5_functions import *
from c6_solar_pv import *

from pathlib import Path
from c7_reward_calc import *
from c8_variables import * 
from c9_RL_functions import * 
import sys,os
from c9a_art_train_functions import * 
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'openai-gym'))
from boptestGymEnv import BoptestGymEnv
import pvlib
from pvlib import pvsystem

import warnings 
warnings.filterwarnings("ignore")
from replay_memory import ReplayMemory
import argparse



updates = 0
parser = argparse.ArgumentParser(description='PyTorch Soft Actor-Critic Args')
parser.add_argument('--env-name', default="HalfCheetah-v2",
                    help='Mujoco Gym environment (default: HalfCheetah-v2)')
parser.add_argument('--policy', default="Gaussian",
                    help='Policy Type: Gaussian | Deterministic (default: Gaussian)')
parser.add_argument('--eval', type=bool, default=True,
                    help='Evaluates a policy a policy every 10 episode (default: True)')
parser.add_argument('--gamma', type=float, default=0.9995, metavar='G',
                    help='discount factor for reward (default: 0.99)')
parser.add_argument('--tau', type=float, default=0.005, metavar='G',
                    help='target smoothing coefficient(τ) (default: 0.005)')
parser.add_argument('--lr', type=float, default=0.00005, metavar='G',
                    help='learning rate (default: 0.0003)')
parser.add_argument('--alpha', type=float, default=0.2, metavar='G',
                    help='Temperature parameter α determines the relative importance of the entropy\
                            term against the reward (default: 0.2)')
parser.add_argument('--automatic_entropy_tuning', type=bool, default=False, metavar='G',
                    help='Automaically adjust α (default: False)')
# parser.add_argument('--seed', type=int, default=123456, metavar='N',
#                     help='random seed (default: 123456)')
parser.add_argument('--batch_size', type=int, default=144*3, metavar='N',
                    help='batch size (default: 256)')
parser.add_argument('--num_steps', type=int, default=1000001, metavar='N',
                    help='maximum number of steps (default: 1000000)')
parser.add_argument('--hidden_size', type=int, default=[1000,1600,1000], metavar='N',
                    help='hidden size (default: 256)')
parser.add_argument('--updates_per_step', type=int, default=10, metavar='N',
                    help='model updates per simulator step (default: 1)')
parser.add_argument('--start_steps', type=int, default=10000, metavar='N',
                    help='Steps sampling random actions (default: 10000)')
parser.add_argument('--target_update_interval', type=int, default=5, metavar='N',
                    help='Value target update per no. of updates per step (default: 1)')
parser.add_argument('--replay_size', type=int, default=1000000, metavar='N',
                    help='size of replay buffer (default: 10000000)')
parser.add_argument('--cuda', action="store_true",
                    help='run on CUDA (default: False)')
args = parser.parse_args()

# ----------------------
# TEST CONTROLLER IMPORTs

'''ACTB Initialize'''

test = False
imit = False
art_training = False
suppress = False
init_path_gen = False
surr_model_activate=False

if test ==True:
    last_ep = 0 
    episodes = len(test_days)
    path = 'RL_Data/01_Normal_run_600_v1_test/'
else:    
    last_ep = 0
    episodes = 2
    path = 'RL_Data/01_Normal_run_600_v1/'



path_NN = path+'02_NN/'

training_batch =12
epochs = 15
steps_forward = 1
sac_int_train = 6
w_guid = 0.0 # 0 for direct run 
n_min_perf = 5 
samples = 50
prob_guided = 0.05  # set to very low number - 


buffer_size=288*100
batch_size = int(144*3)
'''ACTB Initiliaze'''
print('\nRunning controller script...')
 
learning_rate  = 0.00015


if surr_model_activate==True:
        t_sel_keys = np.load('t_sel_keys.npy')
        r_sel_keys = np.load('r_sel_keys.npy')   
        print ("selected keys: {}".format(t_sel_keys, r_sel_keys))
        keys = [t_sel_keys,r_sel_keys]



for episode in range(last_ep+1,last_ep+episodes+1):
    cmd1 = "sudo sysctl vm.drop_caches=1"
    cmd2 = "sudo sysctl vm.drop_caches=2"
    cmd3 = "sudo sysctl vm.drop_caches=3"

    os.system(cmd1);os.system(cmd2);os.system(cmd3)    
    # path = 'RL_Data/02_Online_run_v2/'
    
    state_dim = custom_observation_space.shape[0]
    action_dim = custom_action_space.shape[0]
    hist_min = np.array([min_temp,min_temp])
    hist_max = np.array([max_temp,max_temp])

    score = 0    
    
    agent_2 = SAC(custom_observation_space.shape[0], custom_action_space, args)

    memory = ReplayMemory(args.replay_size)
    
    if test==True: 
        day_no = test_days[episode-1]
        dr_rand_start = test_dr_rand_start[episode-1]
        dr_rand_end = test_dr_rand_end[episode-1]
    else: 
        day_no = np.random.choice(train_days)
        dr_rand_start = round((random.uniform(14.4,16)*5))/5
        dr_rand_end = dr_rand_start + random.uniform(2.5,4.0)
    DR_time = [3600 * dr_rand_start, 3600 * dr_rand_end]
    episode_length = 3600 * 24
    start_time = 24 * 3600 * day_no
    count = 0
    dr_limit = 12000
   
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
                        dr_power_limit=dr_limit,  # in watts
                        DR_event=True,
                        DR_time=DR_time,
                        lower_obs_bounds=lower_obs_bounds,
                        upper_obs_bounds=upper_obs_bounds,                        
                        n_obs=True)

    extra_info = init_extra_info()      

    '''SAC and Surr models Related'''  
    
    if last_ep>0:
        if test==False:
            agent_2.load_checkpoint(ckpt_path=path_NN+"checkpoints/sac_checkpoint_"+str(last_ep)+"_")                                          
    elif test==True:     
        agent_2.load_checkpoint(ckpt_path=path_NN+"checkpoints/sac_checkpoint_"+str(0)+"_")

      
    
        #load surr models 
    '''SAC and Surr models Related'''     

    
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


    '''data for episode'''    
    df = pd.DataFrame(columns=['states','action','next_states','reward','done'],dtype=np.float64)
    '''data for episode'''    

    
    '''Battery Initialize'''
    if test==True:
        cur_soc_n = 0.2
    else:
        cur_soc_n = np.random.uniform(0.1,0.2)

    cur_soc = cur_soc_n* batt_info['batt_cap']
    '''Battery Initialize'''    
      
    agent_state_size = (9,) #env.observation_space.shape       
    states_n = env.reset()

    '''state information'''
    # mean_temp_n : Mean Zone Temperature
    # state_n[5]: Hour of the day 
    # state_n[6]: Current OA 
    # state_n[7]: Forecast OA in 1 hour 
    # state_n[8]: Current HHorIR
    # state_n[9]: Forecasted HHorIR in 1 hour
    # state_n[10]: Countdown to DR
    # state_n[11]: Current DR signal 
    '''state information'''


    '''Main States Pre-processing init state '''  
    states = np.array(states_n)*(upper_obs_bounds-lower_obs_bounds) + lower_obs_bounds
    building_states = env.get_building_states()    
    mean_temp_n = (states_n[0]+states_n[1]+states_n[2]+states_n[3]+states_n[4])/5          
    mean_temp_hist_n = np.array([mean_temp_n,mean_temp_n])  # in celsius 

    
    '''Main States Pre-processing init state'''  

    print ("Last episode: {}".format(last_ep))
    last_ep = episode     
   
    solar_info = {}
    solar_info['day_no'] = day_no
                   

    print("Modified State")

    for i in range(int(episode_length/step)):  
        w_guided = w_guid
        hours = building_states['senHouDec_y']          
        print ("Episode: {}, i: {}, hours: {}, day_no: {}".format(episode,i,hours,day_no))       
        sp = get_sp(hours)[0]
        abs_time = i * step             
        minutes = ((abs_time) % 3600) / 60
        days = math.floor(abs_time / (3600 * 24))                      
        count += 1   
        solar_info['i'] = i     
        mean_temp_hist = hist_min + mean_temp_hist_n*(hist_max-hist_min)  
        print ("mean_temp_hist: {}".format(mean_temp_hist))
                  
        '''Get Building and weather Data'''              
        building_states = env.get_building_states()
        forecasts = env.get_forecast()            
        mean_temp,temp_air,dni,dhi,ghi,w_sp = get_building_weather_data(building_states,forecasts)
        '''Get Building and weather Data'''  
       
                
        '''Agent Related'''
        mean_temp_n = (states_n[0] + states_n[1] + states_n[2] + states_n[3] + states_n[4])/5
        if states_n[10]>0:
            states_n[11] = (dr_rand_end-dr_rand_start)/4
        curr_agent_states_n = np.array([[mean_temp_n,states_n[5],states_n[6],states_n[7],states_n[8],states_n[9],states_n[10],states_n[11],cur_soc_n]])
               
        curr_agent_states = convert_to_state(agent_state_n=curr_agent_states_n ,lower_bnds=agent_lower_obs_bounds,upper_bnds=agent_upper_obs_bounds)

        print ()
        print ("curr agent states n : {}".format(curr_agent_states_n))     
             
        # print ("training with art data")
        
        # print ("replay buffer {};batch_size: {};count: {}; check: {}".format(replay_buffer_mem,batch_size,count,count%training_batch))
        
        
        if i%2==0:
            curr_agent_states_n_600 = curr_agent_states_n                
            df1 = form_curr_df(curr_agent_states_n,mean_temp_hist_n) 
                
            unprocessed_act = agent_2.select_action(state=curr_agent_states_n[0].tolist())
            # print ("unprocessed act: {}".format((w_guided*guided_action)))
            unprocessed_final_action= unprocessed_act 

            df1['action'] = [unprocessed_final_action]
            df1['a1'] = [unprocessed_final_action[0]]
            df1['a2'] = [unprocessed_final_action[1]]         
                    
            print ("unprocessed_f_action: {}".format(unprocessed_final_action))
            # print ("rl_act: {}; unprocessed_f_action: {}".format(unprocessed_act,unprocessed_final_action))

            if cur_soc_n ==0 and unprocessed_act[1]<0:
                r_mod = 200*unprocessed_act[1]
            else:
                r_mod = 0  
 
            processed_action,act_01,act_02 = action_sac_proc_v3(unprocessed_action=unprocessed_final_action)  
        
            print ("processed_action: {}".format(processed_action))
   
        

        '''Advance Simulation'''
        next_states_n,_, done, info = env.step(processed_action)          
        '''Advance Simulation'''    

        ''' PV Lib '''
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

        print (day_no,hours,step)


        ''' Battery Calculation  '''
        plug_power = calc_plug_power(day_no=day_no,sen_hou=hours,step=step)
        building_states = env.get_building_states()
        tot_hvac_pow = building_states['senPowCor_y'] + building_states['senPowPer1_y'] + building_states['senPowPer2_y'] + \
                       building_states['senPowPer3_y'] + building_states['senPowPer4_y'] 
        tot_power = tot_hvac_pow + plug_power
        
        cur_soc,batt_pow_prov,net_grid_power,pow_sold,other_info = battery_calc(act_02=act_02,                                                         
                                                         batt_info = batt_info,
                                                         cur_soc= cur_soc,
                                                         step=step,
                                                         tot_pow=tot_power,
                                                         dc_power=dc_power)   

        print ()        
        print ("Whole building demand: {}; Net Building power: {}".format(tot_power,net_grid_power))
        print ("Batt_pow_prov: {}; Power Sold: {}; PV power: {}; SOC: {}".format(batt_pow_prov,pow_sold,dc_power,cur_soc))                  
        print ()

        net_grid_energy = net_grid_power*step/3600   
        ''' Battery Calculation '''  

        # print ("Power Zone Core: {}, Zone 1: {}, Zone 2: {}, Zone 3: {}, Zone 4: {}".format(building_states['senPowCor_y'],building_states['senPowPer1_y'],building_states['senPowPer2_y'],building_states['senPowPer3_y'],building_states['senPowPer4_y']))

        

        '''Main States Pre-processing'''          
        cur_soc_n = cur_soc/batt_info['batt_cap']         
        next_mean_temp = (building_states['senTemRoom_y']+building_states['senTemRoom1_y'] +building_states['senTemRoom2_y'] +building_states['senTemRoom3_y']+building_states['senTemRoom4_y'])/5
        # print ("next mean temp: {}; mean temp: {}".format(next_mean_temp,mean_temp))
        
        next_mean_temp_n = (next_states_n[0]+next_states_n[1]+next_states_n[2]+next_states_n[3]+next_states_n[4])/5
        if next_states_n[10]>0:
                    next_states_n[11] = (dr_rand_end-dr_rand_start)/4

        next_agent_states_n = np.array([[next_mean_temp_n,next_states_n[5],next_states_n[6],next_states_n[7],next_states_n[8],next_states_n[9],next_states_n[10],next_states_n[11],cur_soc_n]])
        next_agent_states= convert_to_state(agent_state_n=next_agent_states_n,lower_bnds=agent_lower_obs_bounds,upper_bnds=agent_upper_obs_bounds)
        building_states = env.get_building_states()        
        '''Main States Pre-processing''' 
     
        
        ''' mean temp history preprocess'''
        
        # print ("mean temp hist n check 1 : {}".format(mean_temp_hist_n))
        ''' mean temp history preprocess'''

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

        reward,cost,energy_cost,tdisc_cost,ppen_cost,energy_sold_cost,mod_reward,single_reward = calc_reward_function(sen_hou=next_agent_states[0][1],
                                                                                                    DR_time = DR_time,
                                                                                                    next_temp =np.array([next_agent_states[0][0]]),
                                                                                                    individual_rewards= individual_rewards,                                                                                                   
                                                                                                    extra_info=extra_info,
                                                                                                    i=i
                                                                                                    )
        
        reward= reward+r_mod 

       
        # print ("reward: {}; reward_predicted: {}".format(reward,reward_predicted))
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
                          
  
        # print ("mean_temp_hist_n: {}".format(mean_temp_hist_n))  
        # print ("curr_agent_states_600: {}".format(curr_agent_states_n_600))
              
        
        if (i+1)%2==0:    
            memory.push(curr_agent_states_n_600[0], unprocessed_act, reward, next_agent_states_n[0],done) # Append transiti        
            old_mean_temp = curr_agent_states_n_600[0][0]*(max_temp-min_temp)+min_temp    
            delta_T =  next_mean_temp-old_mean_temp    
            t_pred = np.array([delta_T,tot_power/power_scale])
            print ("t_pred: {}, next_mean_temp: {}, old_mean_temp: {}".format(t_pred,next_mean_temp,old_mean_temp))

             

               
            df1['t_pred'] = [t_pred]
            df1['delta_t'] = [delta_T]
            df1['power'] = [tot_power/power_scale]
            df1['reward'] = [reward]
            df1['done'] = [done]
            df1['next_states'] = [next_agent_states_n[0]]

            df = pd.concat([df, df1])   

            print ("t_pred".format(t_pred))
        
            mean_temp_hist = np.insert(mean_temp_hist,0,next_mean_temp)          
            mean_temp_hist = mean_temp_hist[:-1]    
           
        
         
        mean_temp_hist_n = (mean_temp_hist-hist_min)/(hist_max-hist_min) 

        curr_agent_states_n = next_agent_states_n 
        states_n = next_states_n 

        total_cost += cost
        tot_energy_cost += energy_cost
        tot_tdisc_cost  +=  tdisc_cost 
        tot_ppen_cost += ppen_cost
        tot_energy_sold_cost += energy_sold_cost        
        score += reward

               
        print ()
        print ("Total cost: {}".format(total_cost))
             

        

        '''Training Models'''
        replay_buffer_mem = len(memory)
        print ("replay buffer {};batch_size: {};count: {}; check: {}".format(replay_buffer_mem,batch_size,count,count%training_batch))
    

        if count %sac_int_train == 0 and test==False:                      
            if len(memory) > batch_size:
                for e in range(epochs):             
                    critic_1_loss, critic_2_loss, policy_loss, ent_loss, alpha = agent_2.update_parameters(memory, args.batch_size, updates)
                    updates += 1
                    print ("eposhcs: {}".format(e))
                    print ("q_value loss1: {}".format(critic_1_loss))
                    print ("q_value loss2: {}".format(critic_2_loss))
                    print ("policy loss: {}".format(policy_loss))
                    # print ("ent loss: {}".format(ent_loss))   
                    # print ("alpha: {}".format(alpha))   
                    print ()     
                
        '''Training Models'''                
                        
        
        '''Agent Related'''                     
               
        print ()
        print ()
        print("\n");print("\n")

        
        if done:
            # Print KPIs
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
    
            # if test==False and w_guid!=0 :
            #     agent_1.save_models(episode=episode)
            agent_2.save_checkpoint(env_name=episode,
                                     ckpt_path=path_NN+"checkpoints/sac_checkpoint_"+str(episode)+"_")
            
           
            df.to_pickle(path+"04_Mem/mem"+str(episode)+".pkl")           
            env.print_KPIs()
            env.save_episode(filename = path+"03_Data/data_"+str(episode)+".csv",extra_info=extra_info)
            last_ep = episode
            # env.plot_episode(path+"05_Plot/plot_"+str(episode)+".jpg", [0, 1, 2, 3, 4,'tot'])

            
            

            # Print KPIs


print('\nTest case complete.')
# -------------



