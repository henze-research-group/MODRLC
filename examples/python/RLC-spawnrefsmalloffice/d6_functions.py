import pandas as pd
import numpy as np 
import math; import random



state_0,state_1,state_2,state_3 = 6,2,3,5
no_of_states = state_0*state_1*state_2*state_3

cnt = 0 
tab_id = pd.DataFrame(columns=['s0', 's1','s2','s3'],index=range(no_of_states))
for s0 in range (state_0):
  for s1 in range(state_1):   
    for s2 in range(state_2):
      for s3 in range(state_3):        
        tab_id.iloc[cnt]['s1']= s1
        tab_id.iloc[cnt]['s0']= s0
        tab_id.iloc[cnt]['s2']= s2 
        tab_id.iloc[cnt]['s3']= s3
        # tab_id.iloc[cnt]['s4']= s4
        cnt +=1

train_days = [141,149,156,158,159,164,165,166,169,170,171,176,177,178,184,186,188,192,193,198,199,200,204,206,207,208,209,212,214,216,221,232,240,246,253]
test_days = [213,215,247,233,248,185,153]


''' 02 - Battery Model '''
#batt_info = [batt_cap,cha_eff,cha_cont_pow,dis_eff,dis_cont_pow]

def battery_soc(act_frac,cur_soc,batt_info,step):
  old_soc = cur_soc
  if act_frac < 0:
    cur_soc = cur_soc +act_frac*batt_info['dis_cont_pow']*step/3600
    pow_prov = (old_soc-cur_soc)*batt_info['dis_eff']*3600*1000/step
  elif act_frac >0:
    cur_soc = cur_soc +act_frac*batt_info['cha_cont_pow']*step/3600*batt_info['cha_eff']
    pow_prov = -act_frac*batt_info['cha_cont_pow']*1000/batt_info['cha_eff']
  else:
    cur_soc=cur_soc
    pow_prov = 0 

  if cur_soc >= batt_info['batt_cap']:
    cur_soc = batt_info['batt_cap']
  elif cur_soc<=0:
    cur_soc = 0   

  return [cur_soc,pow_prov]


def battery_calc(act_02,act_03,batt_info,cur_soc,step,tot_pow,dc_power):
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
  plug_loads_df = pd.read_csv("RefBldgSmallOfficeBuilding_data.csv")  
  time_plug = int(day_no*24*3600/600 + sen_hou*3600/600)
  plug_loads_df['lights_w'] = plug_loads_df['InteriorLights:Electricity [J](TimeStep)']
  plug_loads_df['equipment_w'] = plug_loads_df['InteriorEquipment:Electricity [J](TimeStep)']
  plug_loads_df['plug_loads_w'] = (plug_loads_df['equipment_w']+plug_loads_df['lights_w'])/step

  plug_power = plug_loads_df['plug_loads_w'].iloc[time_plug]

  return plug_power

def get_dr_index(dr_m1):
  """dr_m1 - countdown signal to dr event - unit is time in hours """
  """dr_0 - if there is a DR event """
  if dr_m1>=3.5:
    dr_index = 7
  elif (dr_m1<3.5)&(dr_m1>=3):
    dr_index = 6
  elif (dr_m1<3)&(dr_m1>=2.5):
    dr_index = 5
  elif (dr_m1<2.5)&(dr_m1>=1.5):
    dr_index = 4 
  elif (dr_m1<1.5)&(dr_m1>=1.0):
    dr_index = 3 
  elif (dr_m1<1.0)&(dr_m1>0.5):
    dr_index = 2 
  elif (dr_m1<0.5)&(dr_m1>0):
    dr_index = 1 
  else:
    dr_index = 0  

  return dr_index 


def get_dr_index_2(dr_m1,dr_0,hour_dec):
  """dr_m1 - countdown signal to dr event - unit is time in hours """
  """dr_0 - if there is a DR event """
  if dr_m1>=3:
    dr_index = 3  
    print ("Condition 3")
  elif (dr_m1<3)&(dr_m1>=1):
    dr_index = 2 
    print ("Condition 2")  
  elif (dr_m1<1.0)&(dr_m1>0):
    dr_index = 1 
    print ("Condition 1")
  elif (dr_m1==0)&(dr_0==1):
    dr_index = 0  
  else:
    dr_index = 3

  if hour_dec>(24-450/3600):
    print ("Condition 4")
    dr_index = 4

  return dr_index 


def get_temp_index(temp):
  temp_ls = np.linspace(20, 26, num=5)

  for index in range(len(temp_ls)):
    if (index==0)&(temp < temp_ls[index]):
      temp_index = index           
    elif (temp<temp_ls[index])&(temp>=temp_ls[index-1]):
      temp_index = index 
    elif (temp>temp_ls[index]):
      temp_index = index    
  return temp_index

def get_time_index(time):
  time_ls = np.linspace(0, 23.5, num=48)
  for index in range(len(time_ls)-1):   
    # print ("Index: {}".format(index))       
    if (time<time_ls[index+1])&(time>=time_ls[index]):    
      # print ("time index 01: {}".format(time_ls[index+1]))    
      # print ("time index 02: {}".format(time_ls[index]))   
      time_index = index       
      
    elif (time>time_ls[index+1]):
      time_index = index +1
  return time_index


def get_oa_index(oa):
  # oa_ls = np.linspace(20,25, num=6)
  oa_ls = np.array([21,24])
  for index in range(len(oa_ls)):
    # print ("Index: {}".format(index))
    if (index==0)&(oa < oa_ls[index]):
      oa_index = index      
    elif (oa<oa_ls[index])&(oa>=oa_ls[index-1]):
      oa_index = index 
    elif (oa>oa_ls[index]):
      oa_index = index
  return oa_index

def get_sp(hour):
  if (hour>=6)&(hour<=22):
    upp_sp = 273.15+24
    low_sp = 273.15+21
  else:
    upp_sp = 273.15+30
    low_sp = 273.15+18
  return [low_sp,upp_sp]

def get_occ_signal(time):
  if (time>6)&(time<=22):
    signal = 1
  else:
    signal = 0 
  return signal

def get_index(s):
  instance = pd.Series({'s0':s[0],'s1':s[1],'s2':s[2],'s3':s[3]})
  id = tab_id.loc[(tab_id==instance).all(axis=1)].index[0]
  return id 

def rbc_controller(hours,mean_T,DR_time):
  start_DR = DR_time[0]/3600
  end_DR = DR_time[1]/3600
  sp  = get_sp(hours) 

  print ("Hours: {}".format(hours))
  print ("Mean Temperature: {}".format(mean_T))
  print ("DR time: {}".format([start_DR,end_DR]))
  print ("SP: {}".format(sp))
  
  if mean_T < sp[0]:
    act=0
    print ("Check 01") 
  elif (mean_T < sp[1])&((hours<start_DR-2)or(hours>end_DR)):
    act=0
    print ("Check 01b") 
  elif (mean_T > sp[0])&((hours>=start_DR-2)&(hours<start_DR)):
    act=1
    print ("Check 01c") 
  elif (mean_T > sp[1])&((hours<start_DR-2)or(hours>end_DR)):
    act=1
    print ("Check 02")   
  elif (hours>= start_DR) & (hours<end_DR):
    act = 0 
    print ("Check 04")    
  return act 

def mem_processor(filename):
    mem_list_1 = pd.read_csv(filename, dtype=object)
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

    return mem_list_1









