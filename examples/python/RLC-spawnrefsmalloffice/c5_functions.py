import pandas as pd
import numpy as np 
import math; import random
import scipy as stats
from scipy.spatial import distance
from scipy.stats import chi2
plug_loads_df = pd.read_csv("RefBldgSmallOfficeBuilding_data.csv")  
from c8_variables import * 

''' 02 - Battery Model '''
#batt_info = [batt_cap,cha_eff,cha_cont_pow,dis_eff,dis_cont_pow]

# added_pv_power: Power added to the battery from PV 
# pv_extra: if pv production is greater than the charging capacity, this is the remaining pv power that couldn't be utilized (applicable only when charging, otherwise zero)
# pow_prov: the power discharged from the battery (-ve means power demanded from the grid)
# used_power: power that is added to the battery from grid

def battery_soc(act_02,added_pv_power,cur_soc,batt_info,step):
  old_soc = cur_soc
  other_info = []
  other_info.append("cur_soc: "+str(cur_soc))
  if act_02 < 0:
    other_info.append("Check b1")
    added_pv_power = 0         
    cur_soc = cur_soc +act_02*batt_info['dis_cont_pow']*step/3600
    if cur_soc<0:
      other_info.append("Check b2")
      cur_soc = 0 
    batt_pow_prov = (old_soc-cur_soc)*batt_info['dis_eff']*3600*1000/step
    pv_extra = 0 
  else:   # condition where power is added to the battery (act_02>0)
    batt_dem= (act_02*batt_info['cha_cont_pow']*1000)/batt_info['cha_eff']   
    other_info.append("batt_dem: "+str(batt_dem))      
    cur_soc = cur_soc + batt_dem*step*batt_info['cha_eff']/(3600*1000)
    other_info.append("Check b3")
    if added_pv_power > batt_dem/batt_info['cha_eff']:  
      other_info.append("Check b4")
      batt_pow_prov=0        
      pv_extra = added_pv_power-batt_dem/batt_info['cha_eff']
    else:
      other_info.append("Check b5")
      batt_pow_prov =  added_pv_power - batt_dem
      pv_extra = 0 

  
  other_info.append("cur_soc: "+str(cur_soc))
  
  if cur_soc >= batt_info['batt_cap']:
    # other_info.append("Check b5a")
    cur_soc = batt_info['batt_cap']  
    batt_pow_prov = (old_soc-cur_soc)*batt_info['cha_eff']*3600*1000/step + added_pv_power

  return cur_soc,batt_pow_prov,pv_extra,other_info

def gen_sample(DR_time,t_h):
  t_zi = np.random.uniform(273.15+16,273.15+36)     
  t_oa_0 = np.random.uniform(-20,15)
  t_oa_1 = t_oa_0 + np.random.uniform(-0.4,0.4)
  h_glo_0= np.random.uniform(0,1000)
  h_glo_1 = h_glo_0 + np.random.uniform(-100,100)          

  dr_m1 = (DR_time[0] - t_h)
  countdown_dr = (DR_time[0] - t_h)

  dr_count_start = 4 

  if countdown_dr>dr_count_start:
      countdown_dr = 0 
  elif countdown_dr<=dr_count_start and countdown_dr>0:
      countdown_dr = dr_count_start - countdown_dr
  else:
      countdown_dr=0 

  dr_m1 = countdown_dr/dr_count_start


  if (t_h>= DR_time[0]) & (t_h<DR_time[1]):
    dr_m0 = 1 
  elif dr_m1>0:
    dr_m0 = DR_time[1] -DR_time[0]
  else: 
    dr_m0 = 0 

  soc = np.random.uniform(0,1)

  agent_states = np.array([t_zi,t_h,t_oa_0,t_oa_1,h_glo_0,h_glo_1,dr_m1,dr_m0,soc])
  agent_states_n = (agent_states - agent_lower_obs_bounds)/(agent_upper_obs_bounds-agent_lower_obs_bounds )

  return agent_states,agent_states_n

def mahalanobis(x=None, data=None, cov=None):
  x_mu = x - np.mean(data)
  print (x_mu)
  if not cov:
        cov = np.cov(data.values.T)
  inv_covmat = np.linalg.inv(cov)
  left = np.dot(x_mu, inv_covmat)
  mahal = np.dot(left, x_mu.T)
  return mahal.diagonal()

def ret_single_t_df(df1):
  df1.reset_index(inplace=True,drop=True)

  df1['delta_t'] = df1['t_pred'].apply(lambda x: x[0])
  df1['power'] = df1['t_pred'].apply(lambda x: x[1])

  df1['a1'] = df1['action'].apply(lambda x: x[0])
  df1['a2'] = df1['action'].apply(lambda x: x[1])


  df1['mean_T'] = df1['states'].apply(lambda x: x[0])
  df1['time'] = df1['states'].apply(lambda x: x[1])
  df1['oa_0'] = df1['states'].apply(lambda x: x[2])
  df1['oa_1'] = df1['states'].apply(lambda x: x[3])
  df1['sol_0'] = df1['states'].apply(lambda x: x[4])
  df1['sol_1'] = df1['states'].apply(lambda x: x[5])
  df1['dr_m1'] = df1['states'].apply(lambda x: x[6])
  df1['dr_m0'] = df1['states'].apply(lambda x: x[7])
  df1['cur_soc'] = df1['states'].apply(lambda x: x[8])
  df1['mean_T_m1'] = df1['mean_T'].shift(1)
  df1 = df1[1:]


  df_t = df1[['mean_T','mean_T_m1','time','oa_0','oa_1','sol_0','sol_1','dr_m1','dr_m0','delta_t','power','a1','a2']]
  df1['mahalanobis'] = mahalanobis(x=df_t, data=df_t)
  df1['p'] = 1 - chi2.cdf(df1['mahalanobis'],len(df_t.columns)-1)
  df_post_T = df1[df1['p']>0.025]
  return df_post_T

def battery_calc(act_02,batt_info,cur_soc,step,tot_pow,dc_power):
  if act_02<0: # Condition 1 - battery discharges +    
    rem_b_power = tot_pow - dc_power
    cur_soc,batt_pow_prov,pv_extra,other_info = battery_soc(act_02=act_02,added_pv_power=0,cur_soc=cur_soc,batt_info=batt_info,step=step)    
    # other_info.append("Check b6") 
    # print ("check b6")
    if rem_b_power<0:
      net_grid_power=0
      net_grid_power = rem_b_power - batt_pow_prov 
    else:
      net_grid_power = rem_b_power - batt_pow_prov       
    
    # print ("net grid power: {}".format(net_grid_power))
    if net_grid_power <0: 
      # other_info.append("Check b7")
      # print ("check b7")
      pow_sold = -net_grid_power
      net_grid_power = 0   
    else:
      pow_sold =0 
  else: # Condition 2 - Battery charges
    cur_soc,batt_pow_prov,pv_extra,other_info = battery_soc(act_02=act_02,added_pv_power=dc_power,cur_soc=cur_soc,batt_info=batt_info,step=step)
    net_grid_power = tot_pow - batt_pow_prov - pv_extra
    # print ("net grid power: {}".format(net_grid_power))
    if net_grid_power < 0:
      # other_info.append("Check b9")
      # print ("check b9")
      pow_sold = -net_grid_power
      net_grid_power = 0   
    else:
      # other_info.append("Check b10")
      # print ("check b10")
      pow_sold = 0 
  return cur_soc,batt_pow_prov, net_grid_power, pow_sold,other_info


def outlier_clearing(df):
  df['states'].iloc[0]
  df["s1"] = df["states"].apply(lambda x: x[0])
  df["s2"] = df["states"].apply(lambda x: x[1])
  df["s3"] = df["states"].apply(lambda x: x[2])
  df["s4"] = df["states"].apply(lambda x: x[3])
  df["s5"] = df["states"].apply(lambda x: x[4])
  df["s6"] = df["states"].apply(lambda x: x[5])
  df["s7"] = df["states"].apply(lambda x: x[6])
  df["s8"] = df["states"].apply(lambda x: x[7])
  df["s9"] = df["states"].apply(lambda x: x[8])
  df["a1"] = df["action"].apply(lambda x: x[0])
  df["a2"] = df["action"].apply(lambda x: x[1])

  df1= df[['s1', 's2', 's3', 's4','s5','s6','s7','s8','s9','a1','a2','reward']]

  df1['mahalanobis'] = mahalanobis(x=df1, data=df1[['s1', 's2', 's3', 's4','s5','s6','s7','s8','s9','a1','a2','reward']])
  df1['p'] = 1 - chi2.cdf(df1['mahalanobis'],11 )

  df = df[df1['p']>0.001]
  return df 


def battery_calc_backup(act_02,act_03,batt_info,cur_soc,step,tot_pow,dc_power):
  '''0 - Battery charge from grid; 1 - Battery charge from PV'''
  
  if act_03==1:     # Charge battery from PV 
    if act_02>0:  # Battery Charge
      bat_pow_dem= act_02*batt_info['cha_cont_pow']*10**3
      cur_soc = battery_soc(act_02,cur_soc,batt_info,step)[0]
      net_grid_power = tot_pow
      print ("Battery power demand: {}".format(bat_pow_dem))
      if bat_pow_dem >= dc_power:
        bat_pow_dem = dc_power
        rem_solar_pv = 0 
        curt_pow = 0 
      elif bat_pow_dem < dc_power:
        rem_solar_pv = (dc_power - bat_pow_dem)
        curt_pow =rem_solar_pv - tot_pow                                         
        if curt_pow <0:
          curt_pow = 0                                                                       
    elif act_02<=0: # Battery Discharge                
      cur_soc = battery_soc(0,cur_soc,batt_info,step)[0]
      curt_pow =  dc_power 
      net_grid_power = tot_pow 
  elif act_03==0:   # Charge battery from grid - normal operation 
    if act_02<=0:   # Battery Discharge
      bat_pow_dem = act_02*batt_info['cha_cont_pow']*10**3
      cur_soc = battery_soc(act_02,cur_soc,batt_info,step)[0] 
      curt_pow =  dc_power 
      net_grid_power = tot_pow + batt_info['dis_eff']*act_02*batt_info['dis_cont_pow']*10**3
    else: #Battery Charge
      bat_pow_dem = act_02*batt_info['cha_cont_pow']*10**3
      print ("Battery power demand: {}".format(bat_pow_dem))            
      cur_soc = battery_soc(act_02,cur_soc,batt_info,step)[0]   
      curt_pow =  dc_power
      net_grid_power = tot_pow + act_02*batt_info['cha_cont_pow']*10**3/batt_info['cha_eff']   

  return cur_soc,curt_pow,net_grid_power 


def calc_plug_power(day_no,sen_hou,step):  
  conv_fact = 1/step
  time_plug = int(day_no*24*3600/step + sen_hou*3600/step)  
  print ("time_plug {}".format(time_plug))
  plug_loads_df['lights_w'] = (plug_loads_df['InteriorLights:Electricity [J](TimeStep)']+plug_loads_df['ExteriorLights:Electricity [J](TimeStep)'])*conv_fact
  plug_loads_df['equipment_w'] = plug_loads_df['InteriorEquipment:Electricity [J](TimeStep)']*conv_fact
  plug_loads_df['plug_loads_w'] = plug_loads_df['equipment_w']+plug_loads_df['lights_w']

  plug_power = plug_loads_df['plug_loads_w'].iloc[time_plug]

  return plug_power

def get_building_weather_data(building_states,forecasts):
  building_obs = ['senTemRoom_y','senTemRoom1_y','senTemRoom2_y','senTemRoom3_y','senTemRoom4_y','senHouDec_y']
  temp_air = forecasts['TDryBul'][0]
  dni = forecasts['HDirNor'][0]
  dhi = forecasts['HDifHor'][0]
  ghi = forecasts['HHorIR'][0]
  w_sp = forecasts['winSpe'][0]
  mean_temp = sum([building_states[i] for i in building_obs[:-1]])/5
  return mean_temp,temp_air,dni,dhi,ghi,w_sp

def action_sac_proc(action):
  act_01 = action[0].numpy() ; act_02 = action[1].numpy() ; act_03=action[2].numpy()  

  print ("unprocessed Action: {}".format([act_01,act_02,act_03]))   

  delta_sp = 5.0 

  flow_zi = 0.15          
  act_sp = 273.15+22.5+act_01*delta_sp

  if act_03>0.5:
    act_03=1
  else:
    act_03=0  

  flow_rate = [flow_zi,flow_zi,flow_zi,flow_zi,flow_zi]
  curr_sp_list = [act_sp,act_sp,act_sp,act_sp,act_sp]
  processed_action = [*curr_sp_list,*flow_rate]

  print ("Action: {}".format([act_01,act_02,act_03])) 
  print ("Current sp list: {}".format(curr_sp_list))

  return processed_action,act_01,act_02,act_03


def action_sac_proc_v2(action):
  act_01 = action[0].numpy() ; act_02 = action[1].numpy() 

  # print ("unprocessed Action: {}".format([act_01,act_02]))   

  delta_sp = 7.5

  flow_zi = 0.15          
  act_sp = 273.15+22.5+act_01*delta_sp

 
  flow_rate = [flow_zi,flow_zi,flow_zi,flow_zi,flow_zi]
  curr_sp_list = [act_sp,act_sp,act_sp,act_sp,act_sp]
  processed_action = [*curr_sp_list,*flow_rate]

  print ("Action: {}".format([act_01,act_02])) 
  print ("Current sp list: {}".format(curr_sp_list))

  return processed_action,act_01,act_02

def action_sac_proc_v3(unprocessed_action):
  act_01 = unprocessed_action[0] ; act_02 = unprocessed_action[1]

  # print ("unprocessed Action: {}".format([act_01,act_02]))   

  delta_sp = 7.5

  flow_zi = 0.15          
  act_sp = 273.15+22.5+act_01*delta_sp

 
  flow_rate = [flow_zi,flow_zi,flow_zi,flow_zi,flow_zi]
  curr_sp_list = [act_sp,act_sp,act_sp,act_sp,act_sp]
  processed_action = [*curr_sp_list,*flow_rate]

  print ("Action: {}; Current sp list: {}".format([act_01,act_02],curr_sp_list)) 
  

  return processed_action,act_01,act_02

def sac_path_storenames(ep):
  actor_name = '00_Actor/actor_'+str(ep)
  critic1_name = '01_Critic1/critic1_'+str(ep)
  critic2_name = '02_Critic2/critic2_'+str(ep)
  value_name = '03_Value/value_'+str(ep)
  target_name ='04_Target/target_'+str(ep)

  return actor_name,critic1_name,critic2_name,value_name,target_name

def init_extra_info():
  extra_info = dict()  
  extra_info['price'] = []   
  extra_info['plug_power'] = []    
  extra_info['pow_sold'] = []
  extra_info['tot_building_power'] = []
  extra_info['score'] = []
  extra_info['net_grid_energy'] = []
  extra_info['net_grid_power'] = []
  extra_info['mod_reward'] = []
  extra_info['r_tdisc'] = []
  extra_info['r_energy'] = []
  extra_info['r_ppen'] = []
  extra_info['r_energy_sold'] = []     
  extra_info['act_02'] = []  
  extra_info['act_01'] = []  
  extra_info['cur_soc'] = [] 
  extra_info['pv_pow'] = [] 
  extra_info['batt_pow_prov']=[]
  extra_info['cost_tdisc']=[]
  extra_info['cost_energy']=[]
  extra_info['cost_ppen']=[]
  extra_info['cost_energy_sold']=[]
  # extra_info['other_info'] = [] 
  return extra_info


def convert_to_state(agent_state_n,lower_bnds,upper_bnds):
  state = agent_state_n*(upper_bnds-lower_bnds)+lower_bnds
  return state

def rbc_action_online(hours,DR_time,sp,cur_soc_n):
  DR_time = np.array(DR_time)/3600
  dr_rand_start = DR_time[0]
  dr_rand_end =  DR_time[1]
  act_01 = sp 

  print ()
  print (hours)
  print ("dr_start: {}".format(dr_rand_start))

  if (hours>(dr_rand_start-2))&(hours<(dr_rand_start)):
    act_02 = 1
  elif (hours > dr_rand_start)&(hours<dr_rand_end):
    act_02 = -1
    if cur_soc_n==0:
      act_01 = act_01-1
  else: 
    act_02 = 0
 
  curr_sp_list = [sp,sp,sp,sp,sp] 
  flow_zi = 0.15    
  flow_rate = [flow_zi,flow_zi,flow_zi,flow_zi,flow_zi]

  processed_action = [*curr_sp_list,*flow_rate]
  processed_action 

  return processed_action,act_01,act_02








