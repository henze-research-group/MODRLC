from variables import * 
import math
import pandas as pd 
import torch 


def create_log_gaussian(mean, log_std, t):
    quadratic = -((0.5 * (t - mean) / (log_std.exp())).pow(2))
    l = mean.shape
    log_z = log_std
    z = l[-1] * math.log(2 * math.pi)
    log_p = quadratic.sum(dim=-1) - log_z.sum(dim=-1) - 0.5 * z
    return log_p

def logsumexp(inputs, dim=None, keepdim=False):
    if dim is None:
        inputs = inputs.view(-1)
        dim = 0
    s, _ = torch.max(inputs, dim=dim, keepdim=True)
    outputs = s + (inputs - s).exp().sum(dim=dim, keepdim=True).log()
    if not keepdim:
        outputs = outputs.squeeze(dim)
    return outputs

def soft_update(target, source, tau):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)

def hard_update(target, source):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(param.data)


def get_index(day_no,sen_hou,time_step):
    return int((((day_no-1)*24 + sen_hou)*3600)/time_step)

def fix_midnight_time(time_str):
    if time_str.endswith('24:00:00'):
        date_str = time_str[:6]  # Extract the date part (e.g., '01/01')
        corrected_time_str = '00:00:00'  # Replace '24:00:00' with '00:00:00'
        return date_str + ' ' + corrected_time_str
    return time_str

def fix_midnight_time(time_str):
    if time_str.endswith('24:00:00'):
        date_str = time_str[:6]  # Extract the date part (e.g., '01/01')
        corrected_time_str = '00:00:00'  # Replace '24:00:00' with '00:00:00'
        return date_str + ' ' + corrected_time_str
    return time_str

def get_sp(hour):
  if (hour>=5)&(hour<=22):
      upp_sp = 273.15+24
      low_sp = 273.15+21
  else:
      upp_sp = 273.15+30
      low_sp = 273.15+15
  return [low_sp,upp_sp]

def get_occupancy(hours):
  if (hours>0)&(hours<6):
        occupancy = 2
  elif (hours>=6)&(hours<8):
      occupancy = 15
  elif (hours >= 8) & (hours <18):
      occupancy = 24
  elif (hours >= 18) & (hours <22):
      occupancy = 15
  else:
      occupancy = 2
  
  return occupancy

def normalize(value,key):
    return (value - min_max[key][0])/(min_max[key][1]-min_max[key][0])

def regularize(value,key):
    return  value*(min_max[key][1]-min_max[key][0])+min_max[key][0]


def normalize_t_state(full_row):
#  print (full_row)
    norm_state = [] 
    value = full_row
    for key in t_model_state_keys:
        value = full_row[key]         
        norm_state.append(normalize(value,key))

    return np.array([norm_state]) 


def calc_thermal_disc(hours,temp,occupancy,Ts):
    if occupancy<50:
        upp_setpoint = 30 
        low_setpoint = 15 
    else:         
        if hours>6 and hours<19:
            upp_setpoint = 24 
            low_setpoint = 21 
        else: 
            upp_setpoint = 30 
            low_setpoint = 15     
    
    if (temp <= upp_setpoint) & (temp>= low_setpoint):
        t_disc = 0
    elif (temp >= upp_setpoint):
        t_disc= (temp - upp_setpoint)* Ts/3600
    else:
        t_disc = (low_setpoint - temp )*Ts/3600

    return t_disc 


def get_energy_price(hours):    
    if hours< 8:
        price = 0.08
    elif hours>=8 and hours <=12:
        price = 0.12
    elif hours>12 and hours < 15: 
        price = 0.2 
    elif hours >=15 and hours < 19:
        price = 0.15
    else:
        price = 0.08   
    return price 


def normalize(value,key):
    norm_value = (value - min_max[key][0])/(min_max[key][1]-min_max[key][0])
    # print ("norm_value: {}".format(norm_value))
    return norm_value

def regularize(value,key):
    return  value*(min_max[key][1]-min_max[key][0])+min_max[key][0]

def normalize_t_state(full_row):
#  print (full_row)
    norm_state = [];reg_state = []
    for key in t_model_state_keys:
        value = full_row[key].values[0]   
        # print ("key: {}; value: {}".format(key,value))   
        # print ("Normalize value: {}".format(normalize(value,key)))
        # print ("norm_state: {}".format(norm_state))
        norm_state.append(normalize(value,key))
        reg_state.append(value)
    
    return reg_state, norm_state

def normalize_appliance_state(full_row):
#  print (full_row)
    norm_state = [] 
    for key in appliances_states_sel:
        value = full_row[key].values[0]   
        # print ("key: {}; value: {}".format(key,value))   
        # print ("Normalize value: {}".format(normalize(value,key)))
        # print ("norm_state: {}".format(norm_state))
        norm_state.append(normalize(value,key))
    
    return norm_state

def normalize_lighting_state(full_row):
#  print (full_row)
    norm_state = [] 
    for key in lighting_states_sel:
        value = full_row[key].values[0]   
        # print ("key: {}; value: {}".format(key,value))   
        # print ("Normalize value: {}".format(normalize(value,key)))
        # print ("norm_state: {}".format(norm_state))
        norm_state.append(normalize(value,key))
    
    return norm_state

def preprocess(action,temp):
    htg = action[0]
    clg = action[1]

    if temp < htg and htg <= clg: 
        clg = min_max['u_cool_stp'][1]
        flag = 1 
    elif htg < temp and temp < clg : 
        htg =  min_max['u_heat_stp'][0]
        clg =  min_max['u_cool_stp'][1]
        flag = 1 
    elif htg <=clg and clg < temp: 
        htg = min_max['u_heat_stp'][0]
        flag  =1 
    else: 
        flag = 0 

    return [htg,clg],flag 

def normalize_action(htg,clg):
    a1 = normalize(htg,'u_heat_stp')
    a2 = normalize(clg,'u_cool_stp')
    return [a1,a2] 

def custom_round(x, base=10):
    return int(base * round(float(x)/base))


def pre_process(df): 
    df = df.rename(columns={'Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)': 'temp_OA',
                            'Environment:Site Outdoor Air Wetbulb Temperature [C](TimeStep)': 'wb_temp_OA',
                            'Environment:Site Outdoor Air Relative Humidity [%](TimeStep)':'rh_OA',
                            'Environment:Site Wind Speed [m/s](TimeStep)': 'wind_speed',
                            'Environment:Site Wind Direction [deg](TimeStep)':'wind_dir',
                            'Environment:Site Horizontal Infrared Radiation Rate per Area [W/m2](TimeStep)':'hir_sol',
                            'Environment:Site Diffuse Solar Radiation Rate per Area [W/m2](TimeStep)':'dif_sol',
                            'Environment:Site Direct Solar Radiation Rate per Area [W/m2](TimeStep)': 'dir_sol',
                            'Environment:Liquid Precipitation Depth [m](TimeStep)': 'liq_prec',
                            'Environment:Site Total Sky Cover [](TimeStep)': 'tot_sky_cov',
                            'Environment:Site Opaque Sky Cover [](TimeStep)': 'opaq_sky_cov',
                            'Environment:Site Exterior Horizontal Sky Illuminance [lux](TimeStep)': 'hor_sky_illum',
                            'Environment:Site Exterior Horizontal Beam Illuminance [lux](TimeStep)': 'hor_beam_illum',                          
                            '0_UNCOND_ZONE:Zone People Occupant Count [](TimeStep)':'Occ_Z0',
                            '1_BOTTOM_ZONE:Zone People Occupant Count [](TimeStep)':'Occ_Z1',
                            '2_MID_ZONE:Zone People Occupant Count [](TimeStep)':'Occ_Z2',
                            '3_UPPER_PENTHOUSE:Zone People Occupant Count [](TimeStep)':'Occ_Z3',                         
                            '1_BOTTOM_ZONE:Zone Thermostat Heating Setpoint Temperature [C](TimeStep)':'u_heat_stp',
                            '1_BOTTOM_ZONE:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)':'u_cool_stp',
                            '0_UNCOND_ZONE:Zone Air Temperature [C](TimeStep)':'Temp_Z0',
                            '1_BOTTOM_ZONE:Zone Air Temperature [C](TimeStep)':'Temp_Z1',
                            '2_MID_ZONE:Zone Air Temperature [C](TimeStep)':'Temp_Z2',
                            '3_UPPER_PENTHOUSE:Zone Air Temperature [C](TimeStep)':'Temp_Z3',
                            'Whole Building:Facility Total HVAC Electricity Demand Rate [W](TimeStep)':'hvac_dem_tot',
                            'Electricity:Facility [J](TimeStep)':'tot_elec',
                            'InteriorLights:Electricity [J](TimeStep)':'elec_lights',
                            'Heating:Electricity [J](TimeStep)':'hvac_heat', 
                            'Cooling:Electricity [J](TimeStep)':'hvac_cool',                          
                            'InteriorEquipment:Electricity [J](TimeStep)': 'elec_equip',
                            'Fans:Electricity [J](TimeStep)':'elec_fans', 
                            'Pumps:Electricity [J](TimeStep)':'elec_pump'}                   
                        )
    
    time_step = 600 
    scale = 66/70

       
    df['tot_elec'] = df['tot_elec']/time_step *scale 
    df['elec_lights'] = df['elec_lights']/time_step * scale 

    df['hvac_heat'] = df['hvac_heat']/time_step * scale 
    df['hvac_cool'] = df['hvac_cool']/time_step *scale 

    df['elec_fans'] = df['elec_fans']/time_step * scale 
    df['elec_pump'] = df['elec_pump']/time_step * scale 
    df['elec_equip'] = df['elec_equip']/time_step * scale     

    df['hvac_dem_tot'] = df['hvac_dem_tot']/1000 #kw conversion
    df['elec_fans'] = df['elec_fans']/1000 #kw conversion
    df['elec_pump'] = df['elec_pump']/1000 #kw conversion
    df['elec_equip'] = df['elec_equip']/1000 #kw conversion
    df['elec_lights']  = df['elec_lights']/1000 
    df['tot_elec'] = df['tot_elec']/1000 
    df['hvac_cool'] = df['hvac_cool']/1000
    df['hvac_heat'] = df['hvac_heat']/1000

    df['appliances_pow'] = df[['elec_equip','elec_pump']].sum(axis=1)

    df[['Occ_Z0','Occ_Z1','Occ_Z2','Occ_Z3']] = df[['Occ_Z0','Occ_Z1','Occ_Z2','Occ_Z3']] * scale 
    df['Occ'] = df[['Occ_Z1','Occ_Z2','Occ_Z3']].sum(axis=1)

    df = df[1008:].reset_index()
    df['Date/Time'] = df['Date/Time'].apply(fix_midnight_time)

    start_date = '2006-01-01'
    end_date = '2007-01-01 00:00:00'
    datetime_range = pd.date_range(start=start_date, end=end_date, freq='10T')
    starting_year = 2006

    df['date_obj'] = datetime_range[1:]

    # df['datetime_obj'] = pd.to_datetime(str(starting_year) + '/' +df['Date/Time'], format='%Y/ %m/%d  %H:%M:%S')
    df['sen_hou'] = df['date_obj'].dt.hour + df['date_obj'].dt.minute/60
    df['day_of_year'] = df['date_obj'].dt.dayofyear
    df['day_no'] = df['date_obj'].dt.dayofyear

    df['day_secs'] = df['sen_hou'].apply(lambda x: int(x * 3600))
    df['date_obj'] = datetime_range[1:]

    df[['sen_hou','tot_elec','Occ_Z0','Occ_Z1','Occ_Z2','Occ_Z3','u_heat_stp','u_cool_stp','Temp_Z0','Temp_Z1','Temp_Z2','Temp_Z3','hvac_dem_tot','hvac_heat','hvac_cool','elec_pump','elec_fans']].head()
    df['Temp_mean_p0'] = df[['Temp_Z1','Temp_Z2','Temp_Z3']].mean(axis=1)

    lag = 1 
    df['Temp_mean_m1'] = df['Temp_mean_p0'].shift(lag)
    df['delta_T'] = df['Temp_mean_p0'] - df['Temp_mean_m1'] 

    df['delta_T'] =  df['delta_T'].shift(-1)
    df['u_heat_stp'] =  df['u_heat_stp'].shift(-1)
    df['u_cool_stp'] =  df['u_cool_stp'].shift(-1)  
    df = df[lag:-1]       
    
    df['tot_secs'] = (df['day_no'] -1)* 3600*24 + df['day_secs']
    df['tot_secs'] = df['tot_secs'].apply(custom_round)

    return df 


def training_override(T,htg,clg,T_oa):
    if T<htg and htg < clg:
        # print ("check 1")
        clg = min_max['u_cool_stp'][1]
        # print ("htg: {}, clg: {}".format(htg,clg))
    elif T>htg and htg<clg:
        # print ("check 2")
        if T_oa> min_max['u_cool_stp'][0]:
            htg = min_max['u_heat_stp'][0]
            # print ("check 3")
        elif T_oa< min_max['u_heat_stp'][0]:
            clg = min_max['u_cool_stp'][1]
            # print ("check 4")
    elif T>clg and htg<clg:
        htg = min_max['u_heat_stp'][0]
        # print ("check 5")
    return htg,clg 



def rl_action_override(T,htg,clg,delta_T):    
    if clg<htg and T<clg:
        htg = clg - delta_T
    elif clg<htg and htg>T and T>clg:
        clg_temp = clg
        clg = htg 
        htg = clg_temp
        return rl_action_override(T,htg,clg,delta_T) 
    elif clg<htg and T>htg:
        clg = htg + delta_T
    elif (clg-htg)<delta_T:
        sigma = delta_T - (clg-htg)
        htg = htg - sigma/2 
        clg = clg + sigma/2

    return htg,clg

def init_extra_info(case_id,batt):
    
    if case_id=="d" or batt==True or case_id=="c":
        keys= ['price','tdisc_cost','energy_cost','tdisc','ener','cost','flag','elec_equip',
            'elec_lights','elec_hvac','u_heat_stp','u_cool_stp','Occ','rewards',
            'unproc_u_heat_stp','unproc_u_cool_stp','X_t','next_states_n','dc_power',
            'net_grid_power','pow_sold','batt_pow_prov','cur_soc','curr_batt_cap','batt_dem']
    else:
        keys= ['price','tdisc_cost','energy_cost','tdisc','ener','cost','flag','elec_equip',
            'elec_lights','elec_hvac','u_heat_stp','u_cool_stp','Occ','rewards',
            'unproc_u_heat_stp','unproc_u_cool_stp','X_t','next_states_n']
        
    extra_info = {key: [0] for key in keys}    
    return extra_info

def sen_hou_to_index(sen_hou): 
     frac =sen_hou%1
     integer = int(sen_hou)
     return integer*6 + math.ceil(frac*60/10) - 1 


def get_scheduled_stp(sen_hou,normalized=True): 
    htg = stp_df.iloc[int(sen_hou_to_index(sen_hou))].htg
    clg = stp_df.iloc[int(sen_hou_to_index(sen_hou))].clg

    if normalized==True:
        htg = (htg - min_max['u_heat_stp'][0])/(min_max['u_heat_stp'][1]-min_max['u_heat_stp'][0])
        clg = (clg - min_max['u_cool_stp'][0])/(min_max['u_cool_stp'][1]-min_max['u_cool_stp'][0])

    return [htg,clg] 


def form_df():         
    return pd.DataFrame(columns=['states','action','next_states','reward','done'],dtype=np.float64)


def init_rtp():
    rng = np.random.default_rng()
    price_rand = rng.uniform(size=(1, 24), low=0.16, high=0.25)[0]*0.8
    # print ("init_price:{}".format(price_rand))
    # print ()
    rtp = [0] * 24
    rtp[0] = price_rand[0]* np.random.uniform(0.5,0.7)  # 0-1
    rtp[1] = price_rand[1]* np.random.uniform(0.6,0.8)     # 1-2
    rtp[2] = price_rand[2]* np.random.uniform(0.6,0.8)      # 2-3
    rtp[3] = price_rand[3]* np.random.uniform(0.7,0.9)     # 3-4
    rtp[4] = price_rand[4]* np.random.uniform(0.7,0.9)       # 4-5
    rtp[5] = price_rand[5]* np.random.uniform(0.7,0.9)     # 5-6
    rtp[6] = price_rand[6]* np.random.uniform(0.7,0.9)       # 6-7
    rtp[7] = price_rand[7]* np.random.uniform(0.8,1.0)       # 7-8
    rtp[8] = price_rand[8]* np.random.uniform(0.8,1.0)       # 8-9
    rtp[9] = price_rand[9]* np.random.uniform(0.9,1.1)       # 9-10
    rtp[10]= price_rand[10]* np.random.uniform(0.9,1.2)       # 10-11
    rtp[11]= price_rand[11]* np.random.uniform(1.0,1.4)       # 11-12           
    rtp[12]= price_rand[12]* np.random.uniform(1.5,1.8)       # 12-13
    rtp[13]= price_rand[13]* np.random.uniform(1.8,2.2)       # 13-14
    rtp[14]= price_rand[14]* np.random.uniform(1.8,2.5)      # 14-15
    rtp[15]= price_rand[15]* np.random.uniform(1.5,2.2)       # 15-16
    rtp[16]= price_rand[16]* np.random.uniform(1.5,1.9)       # 16-17
    rtp[17]= price_rand[17]* np.random.uniform(1.0,1.5)       # 17-18
    rtp[18]= price_rand[18]* np.random.uniform(1.0,1.3)       #18-19
    rtp[19]= price_rand[19]* np.random.uniform(0.9,1.3)      # 19-20
    rtp[20]= price_rand[20]* np.random.uniform(0.9,1.2)       # 20-21
    rtp[21]= price_rand[21]* np.random.uniform(0.7,1.0)       # 21-22
    rtp[22]= price_rand[22]* np.random.uniform(0.5,0.7)       # 22-23
    rtp[23]= price_rand[23]* np.random.uniform(0.5,0.7)        #23-24
    # print (rtp)
    return rtp 

def get_rtp_price(rtp,hour):
    index = int(math.floor(hour))
    return rtp[index]



def add_states(curr_states,hours,rtp,price_obs,other_states=[]):
    states = [] 
    for t in range(len(price_obs)):
        req_time = (hours+price_obs[t])%24
        # print (t,req_time)
        states.append(get_rtp_price(rtp,req_time))

    for o in range(len(other_states)):
        states.append(other_states[o])
    
    curr_states = curr_states + states 
    return curr_states 

def add_ev_states(curr_states,ev_avail_states,batt_state):    
    curr_states = curr_states + ev_avail_states + [batt_state]
    return curr_states 

def get_charging_rate(ev_data,time):
    return ev_data.loc[(ev_data['start_time'] <= time) & (ev_data['end_time'] > time), 'charge'].sum()

def get_discharging_rate(ev_data,time):
    return ev_data.loc[(ev_data['start_time'] <= time) & (ev_data['end_time'] > time), 'discharge'].sum()


def pre_process_6(df):     
    df = df.rename(columns={'Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)': 'temp_OA',
                            'Environment:Site Outdoor Air Wetbulb Temperature [C](TimeStep)': 'wb_temp_OA',
                            'Environment:Site Outdoor Air Relative Humidity [%](TimeStep)':'rh_OA',
                            'Environment:Site Wind Speed [m/s](TimeStep)': 'wind_speed',
                            'Environment:Site Wind Direction [deg](TimeStep)':'wind_dir',
                            'Environment:Site Horizontal Infrared Radiation Rate per Area [W/m2](TimeStep)':'hir_sol',
                            'Environment:Site Diffuse Solar Radiation Rate per Area [W/m2](TimeStep)':'dif_sol',
                            'Environment:Site Direct Solar Radiation Rate per Area [W/m2](TimeStep)': 'dir_sol',
                            'Environment:Liquid Precipitation Depth [m](TimeStep)': 'liq_prec',
                            'Environment:Site Total Sky Cover [](TimeStep)': 'tot_sky_cov',
                            'Environment:Site Opaque Sky Cover [](TimeStep)': 'opaq_sky_cov',
                            'Environment:Site Exterior Horizontal Sky Illuminance [lux](TimeStep)': 'hor_sky_illum',
                            'Environment:Site Exterior Horizontal Beam Illuminance [lux](TimeStep)': 'hor_beam_illum',                          
                            '0_UNCOND_ZONE:Zone People Occupant Count [](TimeStep)':'Occ_Z0',
                            '1ST FLOOR:Zone People Occupant Count [](TimeStep)':'Occ_Z1',
                            '2ND FLOOR:Zone People Occupant Count [](TimeStep)':'Occ_Z2',
                            '3RD-8TH FLOOR:Zone People Occupant Count [](TimeStep)':'Occ_Z3',                         
                            '1ST FLOOR:Zone Thermostat Heating Setpoint Temperature [C](TimeStep)':'u_heat_stp',
                            '1ST FLOOR:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)':'u_cool_stp',
                             '1ST FLOOR:Zone Air Temperature [C](TimeStep)':'Temp_Z1',
                            '3RD-8TH FLOOR:Zone Air Temperature [C](TimeStep)':'Temp_Z3',
                            '2ND FLOOR:Zone Air Temperature [C](TimeStep)':'Temp_Z2',
                            'Whole Building:Facility Total HVAC Electricity Demand Rate [W](TimeStep)':'hvac_dem_tot',
                            'Electricity:Facility [J](TimeStep)':'tot_elec',
                            'InteriorLights:Electricity [J](TimeStep)':'elec_lights',
                            'Heating:Electricity [J](TimeStep)':'hvac_heat', 
                            'Cooling:Electricity [J](TimeStep)':'hvac_cool',                          
                            'InteriorEquipment:Electricity [J](TimeStep)': 'elec_equip',
                            'Fans:Electricity [J](TimeStep)':'elec_fans', 
                            'Pumps:Electricity [J](TimeStep)':'elec_pump'}                   
                        )
    
    time_step = 600 
    scale = 1

       
    df['tot_elec'] = df['tot_elec']/time_step *scale 
    df['elec_lights'] = df['elec_lights']/time_step * scale 
    df['hvac_heat'] = df['hvac_heat']/time_step * scale 
    df['hvac_cool'] = df['hvac_cool']/time_step *scale 

    df['elec_fans'] = df['elec_fans']/time_step * scale 
    df['elec_pump'] = df['elec_pump']/time_step * scale 
    df['elec_equip'] = df['elec_equip']/time_step * scale     

    df['hvac_dem_tot'] = df['hvac_dem_tot']/1000 #kw conversion
    df['elec_fans'] = df['elec_fans']/1000 #kw conversion
    df['elec_pump'] = df['elec_pump']/1000 #kw conversion
    df['elec_equip'] = df['elec_equip']/1000 #kw conversion
    df['elec_lights']  = df['elec_lights']/1000 
    df['tot_elec'] = df['tot_elec']/1000 
    df['hvac_cool'] = df['hvac_cool']/1000
    df['hvac_heat'] = df['hvac_heat']/1000

    df['appliances_pow'] = df[['elec_equip','elec_pump']].sum(axis=1)

    df[['Occ_Z1','Occ_Z2','Occ_Z3']] = df[['Occ_Z1','Occ_Z2','Occ_Z3']] * scale 
    df['Occ'] = df[['Occ_Z1','Occ_Z2','Occ_Z3']].sum(axis=1)

    df = df[1008:].reset_index()
    df['Date/Time'] = df['Date/Time'].apply(fix_midnight_time)

    start_date = '2006-01-01'
    end_date = '2007-01-01 00:00:00'
    datetime_range = pd.date_range(start=start_date, end=end_date, freq='10T')
    starting_year = 2006

    df['date_obj'] = datetime_range[1:]


    # df['datetime_obj'] = pd.to_datetime(str(starting_year) + '/' +df['Date/Time'], format='%Y/ %m/%d  %H:%M:%S')
    df['sen_hou'] = df['date_obj'].dt.hour + df['date_obj'].dt.minute/60
    df['day_of_year'] = df['date_obj'].dt.dayofyear
    df['day_no'] = df['date_obj'].dt.dayofyear

    df['day_secs'] = df['sen_hou'].apply(lambda x: int(x * 3600))
    df['date_obj'] = datetime_range[1:]

    df['Temp_mean_p0'] = df[['Temp_Z1','Temp_Z2','Temp_Z3']].mean(axis=1)

    lag = 1 
    df['Temp_mean_m1'] = df['Temp_mean_p0'].shift(lag)
    df['delta_T'] = df['Temp_mean_p0'] - df['Temp_mean_m1'] 

    df['delta_T'] =  df['delta_T'].shift(-1)
    df['u_heat_stp'] =  df['u_heat_stp'].shift(-1)
    df['u_cool_stp'] =  df['u_cool_stp'].shift(-1)  
    df = df[lag:-1]       
    
    df['tot_secs'] = (df['day_no'] -1)* 3600*24 + df['day_secs']
    df['tot_secs'] = df['tot_secs'].apply(custom_round)

    return df 

def battery_calc(act_02,batt_info,cur_soc,step,tot_pow,dc_power):
  other_info = []
  if act_02<0: # Condition 1 - battery discharges +    
    rem_b_power = tot_pow - dc_power
    cur_soc,batt_pow_prov,pv_extra,cap_exceed_soc = battery_soc(act_02=act_02,added_pv_power=0,cur_soc=cur_soc,batt_info=batt_info,step=step)    
    other_info.append("Check b6") 
    # print ("check b6")
    if rem_b_power<0:
      net_grid_power=0
      net_grid_power = rem_b_power - batt_pow_prov 
    else:
      net_grid_power = rem_b_power - batt_pow_prov       
    
    # print ("net grid power: {}".format(net_grid_power))
    if net_grid_power <0: 
      other_info.append("Check b7")
      # print ("check b7")
      pow_sold = -net_grid_power
      net_grid_power = 0   
    else:
      pow_sold =0 
  else: # Condition 2 - Battery charges
    cur_soc,batt_pow_prov,pv_extra,cap_exceed_soc = battery_soc(act_02=act_02,added_pv_power=dc_power,cur_soc=cur_soc,batt_info=batt_info,step=step)
    net_grid_power = tot_pow - batt_pow_prov - pv_extra
    print ("tot_pow: {}, net grid power: {},batt_pow_prov: {}; pv_extra: {} ".format(tot_pow,net_grid_power,batt_pow_prov,pv_extra))
    if net_grid_power < 0:
      other_info.append("Check b9")
      # print ("check b9")
      pow_sold = -net_grid_power
      net_grid_power = 0   
    else:
      other_info.append("Check b10")
      # print ("check b10")
      pow_sold = 0 
    # print (other_info)
    # print ();print ()
    # print (cur_soc)
  return cur_soc,batt_pow_prov, net_grid_power, pow_sold,cap_exceed_soc

def batt_state_rbc(hours,rtp_0,rtp_1,rtp_2):
    if rtp_2>0.2 or rtp_1>0.2: 
        batt_act = 1.0       
    else:
        batt_act = 0           
    if hours>15:
        batt_act = 0.5 

    if rtp_0 >0.25:
        batt_act = -1  

    if hours>16:
        batt_act = 1 

    return batt_act 

def battery_soc(act_02,added_pv_power,cur_soc,batt_info,step):
    old_soc = cur_soc
    cap_exceed_soc = 0 
    other_info = []
    other_info.append("added_pv_power: "+str(added_pv_power))
    other_info.append("cur_soc: "+str(cur_soc))
    if act_02 < 0:
        other_info.append("Check b1")
        added_pv_power = 0         
        cur_soc = cur_soc +act_02*batt_info['dis_cont_pow']*step/3600
        if cur_soc<0:
            other_info.append("Check b2")
            cur_soc = 0 
        batt_pow_prov = (old_soc-cur_soc)*batt_info['dis_eff']*3600/step
        pv_extra = 0 
    else:   # condition where power is added to the battery (act_02>0)
        batt_dem= (act_02*batt_info['cha_cont_pow'])/batt_info['cha_eff']   
        other_info.append("batt_dem: "+str(batt_dem))      
        cur_soc = cur_soc + batt_dem*step*batt_info['cha_eff']/(3600)
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
        other_info.append("Check b5a")
        cap_exceed_soc = cur_soc 
        cur_soc = batt_info['batt_cap']  
        
        batt_pow_prov = (old_soc-cur_soc)*batt_info['cha_eff']*3600/step + added_pv_power
    # print (other_info)
    return cur_soc,batt_pow_prov,pv_extra,cap_exceed_soc

def form_sel_ev_data(ev_data,time):
    return  ev_data.loc[(ev_data['start_time'] <= time) & (ev_data['end_time'] > time)][:]

def get_total_pv_precal(day_no,i):
    pv_df = pd.read_pickle("0_Data/1_PV/"+str(day_no)+".pkl")
    pv_df.reset_index(drop=True,inplace=True)
    south_pv = pv_df.iloc[i].south_pv
    east_pv = pv_df.iloc[i].east_pv
    west_pv = pv_df.iloc[i].west_pv
    car_port_pv = pv_df.iloc[i].south_pv

    n_south = 84
    n_east = 59
    n_west = 59
    n_car_port = int(10000/1.7) #int(500/1.7)

    return n_south*south_pv + n_east*east_pv + n_west*west_pv + n_car_port*car_port_pv

def get_curr_soc(ev_data,time):
    return ev_data.loc[(ev_data['start_time'] <= time) & (ev_data['end_time'] > time), 'start_soc'].sum()

def get_batt_dem(ev_data,time):
    time = round_down_to_half(time)
    return ev_data[ev_data['end_time']==time]['end_demand'].sum()

def update_ev_data(ev_data,sel_ev_data):
    ev_data.set_index('owner_no', inplace=True)
    sel_ev_data.set_index('owner_no', inplace=True)
    ev_data.update(sel_ev_data)
    ev_data.reset_index(inplace=True)
    return ev_data 

def charge(ev_data,overflow):
    ev_data["charge_frac"] = ev_data["charge"]/ev_data["charge"].sum()
    ev_data['start_soc'] = ev_data['start_soc']+ ev_data["charge_frac"] * overflow
    ev_data['overflow'] = np.where(ev_data['start_soc'] > ev_data['capacity'], ev_data['start_soc'] - ev_data['capacity'],0)
    ev_data['start_soc'] = np.where(ev_data['start_soc'] > ev_data['capacity'], ev_data['capacity'],ev_data['start_soc'])
    return ev_data

def update_overflow_charge(ev_data,overflow):
    i = 0 
    while overflow>0 and overflow<0.0001:
        print ("overflow: {}".format(overflow))
        ev_data = charge(ev_data,overflow)
        overflow = ev_data['overflow'].sum()
        print ()
        print ("start_soc")
        print (ev_data['start_soc'].sum())
        print ("capacity")
        print (ev_data['capacity'].sum())
        i +=1 
        print ("i:{}".format(i))
        if ev_data['start_soc'].sum() == ev_data['capacity'].sum():
            break

    return ev_data

def get_rbc_case4c(sen_hou,rtp_0,rtp_1,rtp_2):
    htg = 15 
    if sen_hou>6 and sen_hou<19: 
        clg = 24
        if rtp_2>0.2:
            clg = 21 
        
        if rtp_0>0.25:
            clg = 24.5 
    else: 
        clg = 30 

    batt_act = batt_state_rbc(sen_hou,rtp_0,rtp_1,rtp_2)

    return [htg,clg,batt_act]

















