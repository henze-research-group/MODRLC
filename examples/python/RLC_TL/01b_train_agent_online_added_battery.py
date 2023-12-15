import b1_sac_agent 
from variables import * 
import numpy as np; import pandas as pd 
from b1_gym_deltaT import GymEnv
# from b1_gym_direct import GymEnv
from b1_sac_agent import SAC
from c1_replay_memory import ReplayMemory
from utils import * 
import warnings 
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import os 

test = False ; rbc = False; test_episode_load = 2000
scheduled_setpoints = False
episode_length = 3600 * 24 #3600 * 24

last_ep = 1700; episodes =300
start_train_ep = 60

if last_ep>0:
     transfer_learning = False

if rbc==True:
     case_id=""
     test = False 
     last_ep=0
     episodes = len(test_days)
     path = '0_Data/Case_'+str(building_id)+str(case_id)+'/' 
     test = False

if test==True:
     last_ep = 0 
     episodes = len(test_days)
     rbc = False

step = 600 
actions = ['u_heat_stp','u_cool_stp'] 
building_obs = ['Temp_mean_p0','Temp_mean_m1','sen_hou']
forecast_obs = {'temp_OA': [0,1],'rh_OA':[0],'hir_sol':[0,1]} 
price_struct = "rtp" 
price_obs = [0,1,2,3]
ev_avail_obs = [0,0.5,1.0,1.5,2.0]

w = {}
w['ener_tot'] = -1 
w['tdisc_tot'] = -1 


dr_obs = None 
kpi_zones = None 
dr_limit = 150000


batch_size = int(144*10)
sac_int_train = 12 ; epochs = 5

key_list = ['Temp_mean_p0','Temp_mean_m1','sen_hou','temp_OA','rh_OA']    # for historian 
extra_list = ['price','tdisc_tot','ener_tot']

rtp_low, rtp_high = 0.05,0.3

state_dim_sac = len(building_obs) + sum(len(v) for v in forecast_obs.values())
sac_act_lower_bnds = [0,0,-1]; sac_act_upper_bnds = [1,1,1]
sac_obs_lower_bnds = np.zeros(state_dim_sac); sac_obs_upper_bnds = np.ones(state_dim_sac)


custom_observation_space = spaces.Box(low = sac_obs_lower_bnds,
                                       high = sac_obs_upper_bnds,
                                       dtype= np.float32) 
custom_action_space = spaces.Box(low  = np.array(sac_act_lower_bnds),
                                       high = np.array(sac_act_upper_bnds),
                                       dtype= np.float32) 




state_dim = custom_observation_space.shape[0] + len(price_obs) + len(ev_avail_obs) + 1 
action_dim = custom_action_space.shape[0]

print ("state_dim: {}, action_dim: {}".format(state_dim,action_dim))

memory = ReplayMemory(args.replay_size)


data = '0_Data/Case_' +str(building_id) +'/comb_data.csv'
agent = SAC(state_dim, custom_action_space, args)


''' Loading agent weights and past memory'''
if last_ep>0:
     memory.load_buffer(save_path=path+"04_Mem/mem"+str(last_ep)+".pkl")


if last_ep>0 and test==False:
     agent.load_checkpoint(ckpt_path=path_NN+"checkpoints/sac_checkpoint_"+str(last_ep)+"_")                                          
elif test==True:     
     agent.load_checkpoint(ckpt_path=path_NN[:-1]+"_test/"+"checkpoints/sac_checkpoint_final")
''' Loading agent weights and past memory'''

if transfer_learning == True:
     agent.load_checkpoint(ckpt_path=path_NN+"checkpoints/sac_checkpoint_"+str(0)+"_")
     

for episode in range(last_ep+1,last_ep+episodes+1):
     if rbc==True or test==True:
          day_no = test_days[episode-1]
     else:
          day_no = np.random.choice(train_days)

     print ("day_no: {}".format(day_no))
     start_time = 24 * 3600 * day_no
     score, count, reward = 0,0,0      
     tot_energy_cost, tot_tdisc_cost, total_cost,tot_ev_penalt_cost,tot_ener_sold_cost = 0,0,0,0,0
     tot_tdisc, tot_energy = 0,0 
     dr_start_time = 13
     dr_end_time = 15 

     dr_duration = dr_end_time-dr_start_time
     extra_info = init_extra_info(case_id=case_id,batt=batt)  

     if price_struct=="rtp":
          rtp = init_rtp()
          if rbc==True:
               with open(path+'03_Data_test/rtp_'+str(episode)+'.txt', 'w') as file:
                    for item in rtp:
                         file.write(str(item) + '\n')
          elif test==True: 
               rtp = []
               with open(path+'03_Data_test/rtp_'+str(episode)+'.txt', 'r') as file:
                    for line in file:
                         rtp.append(int(line.strip()))



     print ("current rtp: ".format(rtp))

     #normalize rtp# 
     rt_n = []
     for el_rtp in rtp:
          x = (el_rtp-rtp_low)/(rtp_high-rtp_low)
          rt_n.append(x)

     rtp_n = rt_n 
  
     env = GymEnv(episode_length=episode_length,
          Ts=step,
          df = data ,
          building_id= building_id,
          extra_info= extra_info,
          start_time=start_time,
          actions=actions,
          building_obs = building_obs, 
          forecast_obs=forecast_obs,                  
          dr_power_limit=dr_limit,  # in watts
          DR_event=True,                                 
          n_obs=True)
     
     '''Battery Initialize'''
     if test==True:
          batt_state_n = 0.2
     else:
          batt_state_n = np.random.uniform(0.1,0.2)

             
     curr_states_n =  env.reset()

     hours = 0  

     ev_avail_states = []
     for ev_hour_forecast in ev_avail_obs:    
          ev_avail_states.append(capacity_per_time[round_down_to_half(hours+ev_hour_forecast)]/full_batt_cap)
   
     #added states 
     curr_states_n = add_states(curr_states=curr_states_n,hours=start_time/3600,rtp=rtp_n,price_obs=price_obs,other_states=[])
     curr_states_n = add_ev_states(curr_states=curr_states_n,ev_avail_states=ev_avail_states,batt_state=batt_state_n)
     curr_states_n = [round(x, 3) for x in curr_states_n]
     curr_batt_soc = get_curr_soc(ev_data,hours)  
     print ("curr_batt_soc: {}".format(curr_batt_soc))

     for i in range(int(episode_length/step)):     
          count+=1        
          env.save_data(key_list)
          hours = env.get_current_value('sen_hou')
          ev_avail_states = []
          for ev_hour_forecast in ev_avail_obs:
               # print (hours+ev_hour_forecast)
               # print (round_down_to_half(hours+ev_hour_forecast))
               ev_avail_states.append(capacity_per_time[round_down_to_half((hours+ev_hour_forecast)%24)]/full_batt_cap)

          
          # print ("ev_avail_states: {}".format(ev_avail_states))
          curr_batt_cap  = capacity_per_time[round_down_to_half(hours)]

          if curr_batt_soc>curr_batt_cap:
               curr_batt_soc = curr_batt_cap

          # print (capacity_per_time)
          print ("curr batt cap: {}".format(curr_batt_cap))          

          ''' Collective battery state''' 
                 
          batt_info['cha_cont_pow'] = get_charging_rate(ev_data,hours)
          batt_info['dis_cont_pow'] = get_discharging_rate(ev_data,hours)
          batt_info['batt_cap'] = curr_batt_cap
          batt_dem = get_batt_dem(ev_data,hours)
          '''Collective battery state '''
               
          print ("Episode: {}, i: {}, hours: {}, day_no: {}".format(episode,i,hours,day_no)) 
          
          # print ("curr states n: {}".format(len(curr_states_n)))
    
          unprocessed_act = agent.select_action(state=curr_states_n)
          batt_act = unprocessed_act[2]  # batt action should range from -1 to 1 

          '''action preprocess stage'''
          T = env.get_current_value('Temp_mean_p0')  
          htg = unprocessed_act[0] * (min_max['u_heat_stp'][1]-min_max['u_heat_stp'][0]) + min_max['u_heat_stp'][0]
          clg = unprocessed_act[1] * (min_max['u_cool_stp'][1]-min_max['u_cool_stp'][0]) + min_max['u_cool_stp'][0]
          
          T_oa = env.get_current_value('temp_OA')

          raw_old = [htg,clg] 

          rtp_0 = get_rtp_price(rtp,hours)
          rtp_1 = get_rtp_price(rtp,(hours+1)%24)
          rtp_2 = get_rtp_price(rtp,(hours+2)%24)  
          

          if rbc==True:                            
               [htg,clg,batt_act] = get_rbc_case4c(hours,rtp_0,rtp_1,rtp_2)

          'Overrides'
          print ("raw stp: {}".format([htg,clg]))
          htg,clg = rl_action_override(T,htg,clg,delta_T)
          print ("htg clg after rl override: {}".format([htg,clg]))


          processed_act = normalize_action(htg,clg)
          processed_act = processed_act+[batt_act]   #adding the batt action

          if price_struct == "tou":
               price = get_energy_price(hours)
          elif price_struct == "rtp": 
               price = get_rtp_price(rtp,hours)


          # print ("rtp: {}, price: {}".format(rtp,price))
 
          occupancy = env.get_current_value('Occ')
          env.KPI_rewards =  {"ener_tot": {"hyper": w['ener_tot']* price *reward_scale , "power": 1},
                              "tdisc_tot": {"hyper": w['tdisc_tot']*tdisc_price * occupancy *reward_scale, "power": 1},
                              "idis_tot": {"hyper": 0, "power": 1},
                              "cost_tot": {"hyper": 0, "power": 1},
                              "emis_tot": {"hyper": 0, "power": 1},
                              "power_pen":{"hyper":-1,  "power":1}}
                          

          if raw_old == [htg,clg]: 
               flag = 0 
          else: 
               flag = 1 

          if scheduled_setpoints==True:
               processed_act = get_scheduled_stp(sen_hou=hours,normalized=True)

          
                    
          '''action preprocess stage'''     
          next_states_n,_, done, info = env.step(processed_act) 

          
          # print ("ev data")          
          
          batt_state_n = curr_batt_soc/full_batt_cap 

          # print ("ev avail states: {}".format(ev_avail_states))

          # print ("rtp: {},price_obs: {}".format(rtp,price_obs))
          next_states_n = add_states(curr_states=next_states_n,hours=hours+step/3600,rtp=rtp_n,price_obs=price_obs,other_states=[])
          # print ("next_states_n after add states: {}".format(next_states_n))
          next_states_n = add_ev_states(curr_states=next_states_n,ev_avail_states=ev_avail_states,batt_state=batt_state_n)

          next_states_n = [round(x, 3) for x in next_states_n]
          # print ("next_states_n after add ev states: {}".format(next_states_n))


                  
          if hours<5 or hours>18.5:
            ac_power = 0 
          else:                       
            # ac_power = get_total_pv(temp_air=temp_air,dni=dni,dhi=dhi,ghi=ghi,w_sp=w_sp)   
            ac_power = get_total_pv_precal(day_no,i)  

          # print ("ac power: {}".format(ac_power))          
          # print ("added next states: {}".format(next_states_n))          

          elec_hvac_pow = env.energy_dict['hvac_pow']
          elec_equip_pow = env.energy_dict['appliances_pow']
          elec_lights_pow = env.energy_dict['lighting_pow']
          tot_pow = elec_hvac_pow + elec_equip_pow + elec_lights_pow #kW 

          dc_power = ac_power*0.98/1000 #kW conversion  

          print (batt_info)

          old_batt_soc = curr_batt_soc  

          print ("batt_action: {}".format(batt_act))
          print ("batt soc changes from: {}".format(curr_batt_soc))  
      
          curr_batt_soc,batt_pow_prov,net_grid_power,pow_sold,cap_exceed_soc = battery_calc(act_02=batt_act,                                                         
                                                         batt_info = batt_info,
                                                         cur_soc= curr_batt_soc,
                                                         step=step,
                                                         tot_pow=tot_pow,
                                                         dc_power=dc_power) 
          
          reward += - net_grid_power * step/3600*price 
          reward += -price_unmet_ev * max((batt_dem-curr_batt_soc),0)
          reward += pow_sold*step/3600 * price 

          reward = reward * reward_scale

          print ("batt soc to: {}".format(curr_batt_soc)) 
          # print ()
          # print (ev_data.head())
          
          """Update ev dataframe"""
          print ()
          sel_ev_data = form_sel_ev_data(ev_data,hours)          
          sel_ev_data = update_overflow_charge(ev_data=sel_ev_data,overflow=cap_exceed_soc-old_batt_soc)       
          # print ("sel ev data: {}".format(sel_ev_data))
          # print (len(sel_ev_data ))
          # print ()
          # print ("sel ev data: {}".format(ev_data))
          # print ()
          
          ev_data = update_ev_data(ev_data,sel_ev_data)
          """Update ev dataframe"""
          
          tdisc = env.kpi_info['tdisc_tot'] 
          ener_from_model = env.kpi_info['ener_tot'] 
        
          ener =  net_grid_power * step/3600 # kWh 
          
          print ("dc power: {}".format(dc_power))
          print ("reward: {}".format(reward))
                    
          tot_tdisc = tot_tdisc+ tdisc 
          tot_energy += ener

          # print ("next_state: {}, reward: {}".format(next_states_n,reward))
          print ("flag: {}; memory len: {}".format(flag,len(memory)))

          if flag ==0: 
               memory.push(curr_states_n, unprocessed_act, reward, next_states_n,done)
               
          elif flag ==1:
               mod_reward = reward - (flag*1000)*reward_scale
               # add modified action
               memory.push(curr_states_n, processed_act, reward, next_states_n,done)
               # add wrong action 
               memory.push(curr_states_n, unprocessed_act, mod_reward, next_states_n,done)    

          "end episode"
          curr_states_n = next_states_n
          score += reward  

          ener_sold = pow_sold* price *step/3600 


                   
          energy_cost = ener * price ; tot_energy_cost += energy_cost
          tdisc_cost = tdisc * tdisc_price * occupancy ; tot_tdisc_cost += tdisc_cost 
          unmet_ev_cost = max(batt_dem-curr_batt_soc,0)* price_unmet_ev
          cost = energy_cost + tdisc_cost + unmet_ev_cost +ener_sold  ; total_cost += cost 

          tot_ev_penalt_cost += unmet_ev_cost
          tot_ener_sold_cost += ener_sold 

          print ("energy: {}; tdisc: {}".format(env.kpi_info['ener_tot'],env.kpi_info['tdisc_tot']))
          print ("tdisc_cost: {}, energy_cost: {}".format(tdisc_cost,energy_cost))
          print ("tot_tdisc_cost: {};tot_energy_cost: {};ener_sold: {}".format(tot_tdisc_cost,tot_energy_cost,ener_sold))
          print ("total cost: {}".format(total_cost))
     
          # print ("extra info"); print (extra_info)   
          extra_info['next_states_n'].append(curr_states_n)
          extra_info['unproc_u_heat_stp'].append(raw_old[0])
          extra_info['unproc_u_cool_stp'].append(raw_old[1])
          extra_info['price'].append(price)
          extra_info['energy_cost'].append(energy_cost)
          extra_info['tdisc_cost'].append(tdisc_cost)
          extra_info['tdisc'].append(tdisc)          
          extra_info['ener'].append(ener)
          extra_info['elec_equip'].append(elec_equip_pow)
          extra_info['elec_lights'].append(elec_lights_pow)
          extra_info['elec_hvac'].append(elec_hvac_pow)
          extra_info['u_cool_stp'].append(info['u_cool_stp'])
          extra_info['u_heat_stp'].append(info['u_heat_stp']) 
          extra_info['Occ'].append(info['Occ'])   
          extra_info['rewards'].append(reward) 
          extra_info['cost'].append(cost)  
          extra_info['flag'].append(flag)  
          extra_info['X_t'].append(info['X_t'])

          extra_info['curr_batt_cap'].append(curr_batt_cap)
          extra_info['net_grid_power'].append(net_grid_power)
          extra_info['pow_sold'].append(pow_sold)
          extra_info['batt_pow_prov'].append(batt_pow_prov)
          extra_info['cur_soc'].append(curr_batt_soc)
          extra_info['batt_dem'].append(batt_dem)
          extra_info['dc_power'].append(dc_power)


         

     
          '''training '''    

          if count %sac_int_train == 0 and test==False and rbc==False:                      
               if len(memory) > args.batch_size and episode>start_train_ep:
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
                  
               
          print ('\n')
          print ('\n')
          if done: 
               print ("check 1")               
               KPI_hist['episodes'].append(episode)
               KPI_hist['scores'].append(score)
               KPI_hist['total_cost'].append(total_cost)
               KPI_hist['energy_total_cost'].append(tot_energy_cost)
               KPI_hist['tdisc_total_cost'].append(tot_tdisc_cost)  
               KPI_hist['ener_tot'].append(tot_energy)
               KPI_hist['tdisc_tot'].append(tot_tdisc)  
               KPI_hist['DR_start_time'].append(dr_start_time)
               KPI_hist['DR_end_time'].append(dr_end_time)
               KPI_hist['DR_duration'].append(dr_duration )
               KPI_hist['day_no'].append(day_no)
               KPI_hist['ev_penalt_cost'].append(tot_ev_penalt_cost)
               KPI_hist['ener_sold_cost'].append(tot_ener_sold_cost)
               # print (KPI_hist)
               KPI_df = pd.DataFrame.from_dict(KPI_hist)
               memory.save_buffer(suffix="", save_path=path+"04_Mem/mem"+str(episode)+".pkl")
               if test==False:
                    KPI_df.to_csv(path+"01_KPI/"+"KPI_" + str(episode) + "_SAC.csv")  
                    # df.to_pickle(path+"04_Mem/mem"+str(episode)+".pkl")   
                    if episode%20==0:
                         agent.save_checkpoint(env_name=episode,ckpt_path=path_NN+"checkpoints/sac_checkpoint_"+str(episode)+"_")
                    env.save_data(key_list = key_list)
                    env.save_historian(extra_info=extra_info,location = path + "03_Data/historian_data_"+str(episode)+'.csv')
               else:
                    KPI_df.to_csv(path+"01_KPI_test/"+"KPI_" + str(episode) + "_SAC.csv")  
                    # df.to_pickle(path+"04_Mem/mem"+str(episode)+".pkl")   
                    env.save_data(key_list = key_list)
                    env.save_historian(extra_info=extra_info,location = path + "03_Data_test/historian_data_"+str(episode)+'.csv')

               last_ep = episode
               








