
import requests
import numpy as np;import pandas as pd
import gym
from gym import spaces
import collections
from collections import OrderedDict
import math; import random; from statistics import mean
from c3d_SAC import Agent
from c5_functions import *
from c6_solar_pv import *
from pathlib import Path
from c7_reward_calc import *
from c8_variables import * 
from c9_RL_functions import * 
from c9a_art_train_functions import * 
from c2_surrogate_models import temperature_model,reward_model
from c4_LSTM_search import Agent_search
import sys,os
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'openai-gym'))
from boptestGymEnv import BoptestGymEnv
import pvlib
from pvlib import pvsystem
import warnings
warnings.filterwarnings("ignore")


# ----------------------
# TEST CONTROLLER IMPORTs

'''ACTB Initialize'''


last_ep =14
episodes = 1
training_batch = 24
surr_train_epochs,epochs = 15,5
# look_forward = 10/60 #in hours 
steps = 1 #int(look_forward*3600/600)
sac_int_train = 6
w_guid = 0.3
n_min_perf = 15
prob_guided = 0.00000001 #0.1
suppress = False
dr_limit = 12000
samples = 50
buffer_size=288*100

#     t_model = temperature_model(state_size=6,pred_size=2,
#                     batch_size=5,buffer_size=buffer_size,lr=learning_rate[0])  

#     r_model  = reward_model(state_size=9,pred_size=1,
#                 batch_size=5,buffer_size=buffer_size,lr=learning_rate[1])  
    
#     r_model.model_load_weights(name=path_NN+'05_Surr_Models/r_model_'+str(last_ep)+'.h5')
#     t_model.model_load_weights(name=path_NN+'05_Surr_Models/t_model_'+str(last_ep)+'.h5')

'''ACTB Initiliaze'''
print('\nRunning controller script...')

learning_rate  = [0.00008,0.0001]
agent_search = Agent_search(batch_size=144*10,buffer_size=144*100,lr=learning_rate)
batch_size = int(144*5)

for episode in range(last_ep+1,last_ep+episodes+1):
    cmd1 = "sudo sysctl vm.drop_caches=1"
    cmd2 = "sudo sysctl vm.drop_caches=2"
    cmd3 = "sudo sysctl vm.drop_caches=3"

    os.system(cmd1)
    os.system(cmd2)
    os.system(cmd3)

    
    path = 'RL_Data/01_Online_run_guid_600/'

    state_dim = custom_observation_space.shape[0]
    action_dim = custom_action_space.shape[0]
    hist_min = np.array([min_temp,min_temp,min_temp])
    hist_max = np.array([max_temp,max_temp,max_temp])
    score = 0    
    agent = Agent(action_dim, state_dim, hidden_dim=[500,800,500],replay_buffer_size=288*400,path=path)
    day_no = np.random.choice(train_days)
    dr_rand_start = random.uniform(14.5,18)
    dr_rand_end = dr_rand_start + random.uniform(1.5,3.0)
    DR_time = [3600 * dr_rand_start, 3600 * dr_rand_end]
    episode_length = 3600 * 24
    start_time = 24 * 3600 * day_no
    count = 0
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
    path_NN = path+'02_NN/'  
    if last_ep>0:
        print ("loading weights")
        agent.load_models(episode=last_ep) 
        agent_search.load_model_data(episodes=last_ep,path=path)
        agent_search.load_weights(t_model_weights=path_NN+'05_Surr_Models/t_model_'+str(last_ep)+'.h5',
                                  r_model_weights=path_NN+'05_Surr_Models/r_model_'+str(last_ep)+'.h5')
        agent.load_data(episodes=last_ep,path=path)

        #load surr models 
    '''SAC and Surr models Related'''     


    '''data for episode'''
    df = pd.DataFrame(columns=['states','action','next_states','reward','done',
                                't_state','t_pred','r_state','r_pred'],dtype=np.float64)
    '''data for episode'''    

    
    '''Battery Initialize'''
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
    mean_temp_hist_n = np.array([mean_temp_n,mean_temp_n,mean_temp_n])  # in celsius 

    print ("mean_temp_hist_n: {}".format(mean_temp_hist_n))
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
                  
        '''Get Building and weather Data'''              
        building_states = env.get_building_states()
        forecasts = env.get_forecast()            
        mean_temp,temp_air,dni,dhi,ghi,w_sp = get_building_weather_data(building_states,forecasts)
        '''Get Building and weather Data'''  
       
                
        '''Agent Related'''
        mean_temp_n = (states_n[0] + states_n[1] + states_n[2] + states_n[3] + states_n[4])/5
        curr_agent_states_n = np.array([[mean_temp_n,states_n[5],states_n[6],states_n[7],states_n[8],states_n[9],states_n[10],states_n[11],cur_soc_n]])
        
        # if i==0: 
        #     unprocessed_act = agent.get_action(curr_agent_states_n[0])  
        #     processed_action,act_01,act_02 = action_sac_proc_v3(unprocessed_action=unprocessed_final_action)  
        #     r_mod = 0 

        if (i)%2==0:
            curr_agent_states_n_600 = curr_agent_states_n
            unprocessed_act = agent.get_action(curr_agent_states_n[0])    
            df_path = agent_search.gen_trajectory(samples=samples,
                                    steps_forward=steps,
                                    curr_agent_states_n=curr_agent_states_n,
                                    forecasts=forecasts,                                    
                                    mean_temp_hist_n=mean_temp_hist_n,
                                    DR_time=DR_time,
                                    solar_info=solar_info)

            print (df_path[['r1','s1','action_1']][0:45])

            guided_action = agent_search.find_opt_first_action(df=df_path)
            # guided_action = np.array([0,0])

            

            if np.random.uniform(0,1)<prob_guided:
                w_guided =w_guid
                print ("RL overriden")
            else:
                w_guided = 1
            
            unprocessed_final_action= (1-w_guided)*unprocessed_act + w_guided*guided_action 
            print ("guided action: {}; rl_act: {}; unprocessed_f_action: {}".format(guided_action,unprocessed_act,unprocessed_final_action))

        # print ("df_path {}".format(df_path[['s1','r1','a1','s2','r2','a2']].head()))

            if cur_soc==0 and unprocessed_act[1]<0:
                # unprocessed_act = [unprocessed_act[0],0]
                r_mod = 200*unprocessed_act[1]
            else:
                r_mod = 0 

        print ()
        print ("curr agent states n : {}".format(curr_agent_states_n))        
            
              
        processed_action,act_01,act_02 = action_sac_proc_v3(unprocessed_action=unprocessed_final_action)  

        # """ online artificial training"""
        # """-----------------"""
        # if (i+1)%2==0:
        #     steps_forward = min(3,288-i-1)
        #     print ("steps forward")

                                   

        #     for sample in range(20):   
        #         art_curr_agent_states_n = curr_agent_states_n               
        #         df,reward_names,column_names = init_df(steps_forward=steps_forward)

        #         for key in forecasts.keys():
        #             forecasts[key] = np.repeat(forecasts[key],int(3600/600)).tolist()

        #         mean_temp_hist = mean_temp_hist_n*(max_temp-min_temp)+min_temp 
        #         art_mean_temp_hist_n = mean_temp_hist_n   
        #         art_mean_temp_hist = mean_temp_hist

        #         print ();print ()           
        #         for art_step in range(steps_forward):
        #             action_index = np.random.choice(action_indexes)   
        #             rl_act = agent.get_action(art_curr_agent_states_n[0])   
        #             exp_action = get_action_from_index(action_index)    

        #             beta_1 = np.random.uniform(0.9,1)
        #             art_action = beta_1* rl_act + (1-beta_1)*exp_action 
                    
        #             if suppress==False:
        #                     print ("sample: {}; step: {}; curr_agent_states_n: {}".format(sample,art_step,art_curr_agent_states_n ))  
        #                     print ("rl_act: {}; exp_action: {}; art_action: {}".format(rl_act,exp_action,art_action))                  
        #             t_state,r_state = form_curr_r_and_t_state(curr_agent_states_n=art_curr_agent_states_n,action=art_action,mean_temp_hist_n=art_mean_temp_hist_n)
                                        
        #             r_state_n = normalize_r_state(r_state)
        #             t_state_n = normalize_t_state(t_state)                  
                    
        #             art_reward = r_model.predict(input_state=r_state_n)[0][0]

                                    
        #             ''' form next state'''                    
        #             delta_T = t_model.predict(input_state=t_state_n)[0][0]
        #             tot_pow_p = t_model.predict(t_state_n)[0][1]*power_scale 
        #             print ("delta_T: {}; art_action: {},art_reward".format(delta_T,art_action,art_reward))

        #             print ("r_state: {}".format(r_state_n))
        #             print ("t_state: {}".format(t_state_n))
        #             art_curr_agent_states, art_mean_temp_hist = form_next_agent_state(r_state_n=r_state_n,
        #                                                             t_state_n=t_state_n,
        #                                                             action=art_action,
        #                                                             step=art_step+1,
        #                                                             forecasts=forecasts,
        #                                                             delta_T = delta_T,
        #                                                             mean_temp_hist=art_mean_temp_hist,
        #                                                             DR_time=DR_time,
        #                                                             solar_info=solar_info,
        #                                                             tot_pow=tot_pow_p)  
        #             art_next_agent_states_n = (art_curr_agent_states-gen_low_bounds)/(gen_upp_bounds-gen_low_bounds)

        #             agent.remember(art_curr_agent_states_n[0],art_action,art_reward,art_next_agent_states_n[0],False)
        #             art_curr_agent_states_n = art_next_agent_states_n
        #             print ()

        # """ online artificial training"""
        """ -------------"""

        # q_value_loss1_l,q_value_loss2_l,value_loss_l,policy_loss_l = agent.train(batch_size=batch_size,epochs=epochs)




        ''' Guided action'''


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
        plug_power = calc_plug_power(day_no=day_no,sen_hou=hours,step=300)
        building_states = env.get_building_states()
        tot_hvac_pow = building_states['senPowCor_y'] + building_states['senPowPer1_y'] + building_states['senPowPer2_y'] + \
                       building_states['senPowPer3_y'] + building_states['senPowPer4_y'] 
        tot_power = tot_hvac_pow + plug_power
        
        next_soc,batt_pow_prov,net_grid_power,pow_sold,other_info = battery_calc(act_02=act_02,                                                         
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

        print ("Power Zone Core: {}, Zone 1: {}, Zone 2: {}, Zone 3: {}, Zone 4: {}".format(building_states['senPowCor_y'],building_states['senPowPer1_y'],building_states['senPowPer2_y'],building_states['senPowPer3_y'],building_states['senPowPer4_y']))

        
        '''Main States Pre-processing'''          
        next_soc_n = next_soc/batt_info['batt_cap']         
        next_mean_temp = (building_states['senTemRoom_y']+building_states['senTemRoom1_y'] +building_states['senTemRoom2_y'] +building_states['senTemRoom3_y']+building_states['senTemRoom4_y'])/5
        # print ("next mean temp: {}; mean temp: {}".format(next_mean_temp,mean_temp))
        
        next_mean_temp_n = (next_states_n[0]+next_states_n[1]+next_states_n[2]+next_states_n[3]+next_states_n[4])/5
        next_agent_states_n = np.array([[next_mean_temp_n,next_states_n[5],next_states_n[6],next_states_n[7],next_states_n[8],next_states_n[9],next_states_n[10],next_states_n[11],cur_soc_n]])
        next_agent_states= convert_to_state(agent_state_n=next_agent_states_n,lower_bnds=agent_lower_obs_bounds,upper_bnds=agent_upper_obs_bounds)
        building_states = env.get_building_states()
        
        '''Main States Pre-processing'''  
    
        # print ("next_state_n: {}".format(next_states_n))
        # print ("next_agent_state_n: {}".format(next_agent_states_n))           
        
        ''' mean temp history preprocess'''
        mean_temp_hist = np.insert(mean_temp_hist,0,next_mean_temp)
        mean_temp_hist = mean_temp_hist[:-1]

        # print ("mean_temp_hist: {}".format(mean_temp_hist))  
        mean_temp_hist_n = (mean_temp_hist - hist_min)/(hist_max-hist_min)
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
        
        reward = reward+r_mod
        
        # print ("mod reward: {}".format(mod_reward))  
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
                          
        '''t and r model state setup'''


        if (i+1)%2==0:
            old_mean_temp = curr_agent_states_n_600[0][0]*(max_temp-min_temp)+min_temp
            t_state,r_state = form_curr_r_and_t_state(curr_agent_states_n=curr_agent_states_n_600,action=unprocessed_final_action,mean_temp_hist_n=mean_temp_hist_n)
            r_state_n = normalize_r_state(r_state)
            t_state_n = normalize_t_state(t_state)
            t_pred = np.array([next_mean_temp-old_mean_temp,tot_power/power_scale])        
            print ("next mean temp: {}; mean temp: {}, t_pred: {}; reward: {}".format(next_mean_temp,mean_temp,t_pred,reward))
            agent_search.append_model_sample(t_state_n=t_state_n[0],t_pred=t_pred,r_state_n=r_state_n[0],r_pred=reward)
            agent.remember(curr_agent_states_n_600[0],unprocessed_final_action,reward,next_agent_states_n[0],done)        
            df1 = pd.DataFrame({'states':[curr_agent_states_n_600[0]],'action':[unprocessed_final_action],'next_states':[next_agent_states_n[0]],'reward':[reward],'done':[done],'t_state':[t_state_n[0]],'t_pred':[t_pred],'r_state':[r_state_n[0]],'r_pred':[reward]})
            df = pd.concat([df, df1])   
            mean_temp_hist = np.insert(mean_temp_hist,0,next_mean_temp)
            mean_temp_hist = mean_temp_hist[:-1]
        '''t and r model state setup'''      

        #print ("extra info after reward calc: {}".format(extra_info))  
        mean_temp_hist_n = (mean_temp_hist-hist_min)/(hist_max-hist_min)
        curr_agent_states_n = next_agent_states_n 
        states_n = next_states_n 
        cur_soc = next_soc
        cur_soc_n = next_soc_n 

        total_cost += cost
        tot_energy_cost += energy_cost
        tot_tdisc_cost  +=  tdisc_cost 
        tot_ppen_cost += ppen_cost
        tot_energy_sold_cost += energy_sold_cost        
        score += reward

        # for x in range(n_min_perf):
        #     df_path,df_state,df_next_state,df_action,df_reward = agent_search.min_states(df=df_path)
        #     agent.remember(df_state[0],unprocessed_final_action,df_reward,df_next_state[0],False) 
        
        print ("Total cost: {}".format(total_cost))
        '''Agent Related'''              
        

        '''Training Models'''
        replay_buffer_mem = agent.buffer_mem()
        print ("replay buffer {};batch_size: {};count: {}; check: {}".format(replay_buffer_mem,batch_size,count,count%training_batch))
        if count % training_batch == 0:
            agent_search.train_surr_models(epochs=surr_train_epochs)            
            if replay_buffer_mem > batch_size:
                print ("training in progress")                 
                print ()   
           
            
        
        if count %sac_int_train == 0:                      
            if replay_buffer_mem > batch_size:
                print ("training in progress")
                q_value_loss1_l,q_value_loss2_l,value_loss_l,policy_loss_l = agent.train(batch_size=batch_size,epochs=epochs)
                print ("q_value loss1: {}".format(q_value_loss1_l))
                print ("q_value loss2: {}".format(q_value_loss2_l))
                print ("value loss: {}".format(value_loss_l))
                print ("policy loss: {}".format(policy_loss_l))   
                print () 
        '''Training Models'''                
                        
        
        '''Agent Related'''                     
               
        print ()
        print ()
        print("\n")

        
        if done:
            # Print KPIs
            kpi = (env.get_KPIs())
            for kpi_name in kpi_list:
                KPI_hist[kpi_name].append(kpi[kpi_name])

            agent_search.save_weights(t_model_weights=path_NN+'05_Surr_Models/t_model_'+str(episode)+'.h5',
                                      r_model_weights=path_NN+'05_Surr_Models/r_model_'+str(episode)+'.h5')            
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
            
            agent.save_models(episode=episode)
            df.to_pickle(path+"04_Mem/mem"+str(episode)+".pkl")           
            env.print_KPIs()
            env.save_episode(filename = path+"03_Data/data_"+str(episode)+".csv",extra_info=extra_info)
            # env.plot_episode(path+"05_Plot/plot_"+str(episode)+".jpg", [0, 1, 2, 3, 4,'tot'])

            
            

            # Print KPIs


print('\nTest case complete.')
# -------------



