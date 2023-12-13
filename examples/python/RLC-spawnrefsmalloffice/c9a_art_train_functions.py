import pandas as pd 
from c8_variables import * 
from c5_functions import * 

suppress = True

lower_r_bounds = np.array([[min_temp, 0,min_oa,min_sol,min_dr,min_dr,min_batt,0,0]]) 
upper_r_bounds = np.array([[max_temp,24,max_oa,max_sol,max_dr,max_dr,max_batt,1, 1]])
lower_t_bounds = np.array([[min_temp,min_temp, 0,min_oa,min_sol,0]]) 
upper_t_bounds = np.array([[max_temp,max_temp,24,max_oa,max_sol,1]])

gen_low_bounds = np.array([min_temp, 0,min_oa,min_oa,min_sol,min_sol,0, 0, 0])
gen_upp_bounds = np.array([max_temp,24,max_oa,max_oa,max_sol,max_sol,1, 1, 1]) 

a1_guides = np.array([-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1.0])
a2_guides = np.array([-1,-0.5,0.0,0.5,1.0])
a1_dim = len(a1_guides)
a2_dim = len(a2_guides)

action_id = pd.DataFrame(columns=['a1', 'a2'],index=range(a1_dim*a2_dim))
action_dim = np.array([a1_dim,a2_dim])
cnt = 0 

for a1_index in range(a1_dim):
  for a2_index in range(a2_dim):
    action_id.iloc[cnt]['a1'] = a1_index
    action_id.iloc[cnt]['a2'] = a2_index
    cnt+=1 

action_id.reset_index(inplace=True)
action_id = action_id.rename(columns={"index": "action_index"})

action_indexes = len(action_id) #total no of possible actions 

def init_df(steps_forward):
    reward_names = []
    action_names = []
    state_names = []
    for step in range(steps_forward):
        action_names.append('a'+str(step+1))
        reward_names.append('r'+str(step+1))
        state_names.append('s'+str(step+1))

    column_names = reward_names + action_names + state_names
    
    df = pd.DataFrame(columns=column_names)
    return df,reward_names,action_names


def scale_r_state(r_state_n):                    
    r_state = r_state_n*(upper_r_bounds-lower_r_bounds)+lower_r_bounds
    return r_state 

def normalize_r_state(r_state): 
    r_state_n = (r_state - lower_r_bounds)/(upper_r_bounds-lower_r_bounds)
    return r_state_n

def scale_t_state(t_state_n):  
    t_state = t_state_n*(upper_t_bounds-lower_t_bounds)+lower_t_bounds
    return t_state 

def normalize_t_state(t_state): 
    t_state_n = (t_state - lower_t_bounds)/(upper_t_bounds-lower_t_bounds)
    return t_state_n   

def form_curr_r_and_t_state(curr_agent_states_n,mean_temp_hist_n,action):           
    mean_temp_n = curr_agent_states_n[0][0]
    mean_temp_n_m1 = mean_temp_hist_n[1]
    hour_n = curr_agent_states_n[0][1]
    oa_n = curr_agent_states_n[0][2]   
    sol_n= curr_agent_states_n[0][4]   
    dr_m1 = curr_agent_states_n[0][6]          
    dr_m0 = curr_agent_states_n[0][7]         
    soc_n = curr_agent_states_n[0][8]          
    
    act_1 = action[0]
    act_2 = action[1]

    r_state_n = np.array([[mean_temp_n,hour_n,oa_n,sol_n,dr_m1,dr_m0,soc_n,act_1,act_2]])
    t_state_n = np.array([[mean_temp_n_m1,mean_temp_n,hour_n,oa_n,sol_n,act_1]]) 

    t_state = scale_t_state(t_state_n)
    r_state = scale_r_state(r_state_n)    

    if suppress==False:
        print ("t_state: {}; t_state_n: {}".format(t_state,t_state_n))
        print ("r_state: {}; r_state_n: {}".format(r_state,r_state_n))
        
    
    return t_state, r_state

def get_action_from_index(action_index):
    a1_index= action_id[action_id['action_index']==action_index].a1.item()
    a2_index= action_id[action_id['action_index']==action_index].a2.item()
    act = np.array([a1_guides[a1_index],a2_guides[a2_index]])
    return act

def init_act_pso(dimensions,steps):
  action_pso = []
  for _ in range(steps):
    act = []
    for _ in range(dimensions):
        act.append(np.random.uniform(-1,1))    
    action_pso.append(act)
  return action_pso

def get_total_pv_precal(day_no,i):
    pv_df = pd.read_pickle("RL_Data/00_General/01_PV/"+str(day_no)+".pkl")
    pv_df.reset_index(drop=True,inplace=True)
    south_pv = pv_df.iloc[i].south_pv
    east_pv = pv_df.iloc[i].east_pv
    west_pv = pv_df.iloc[i].west_pv
    car_port_pv = pv_df.iloc[i].south_pv

    n_south = 84
    n_east = 59
    n_west = 59
    n_car_port = 300 #int(500/1.7)

    return n_south*south_pv + n_east*east_pv + n_west*west_pv + n_car_port*car_port_pv

def form_next_agent_state(art_curr_agent_states,action,step,forecasts,mean_temp_hist,delta_T,DR_time,solar_info,tot_pow):
    # print ("t_state_n: {}".format(t_state_n))
    # tot_pow = self.t_model.predict(np.array([t_state_n]))         
       
    next_mean_temp = art_curr_agent_states[0][0] + delta_T    
    # print ("next_mean_temp : {}, curr_curr_agent_states: {}".format(next_mean_temp,art_curr_agent_states))      
    next_hour = (art_curr_agent_states[0][1]+600/3600)%24
    next_oa = forecasts['TDryBul'][step]  
    next_oa_f1 = forecasts['TDryBul'][step+12] 
    next_sol= forecasts['HHorIR'][step]  
    next_sol_f1 = forecasts['HHorIR'][step+12] #implement proper
    DR_time_h = np.array(DR_time)/3600

    if (next_hour>= DR_time_h[0])&(next_hour<=DR_time_h[1]):
        next_dr_m0 = 1
    else:
        next_dr_m0 = 0 

    next_dr_m1 = (DR_time_h[0]-next_hour)/16
    if next_dr_m1<0:
        next_dr_m1 = 0   
    next_act_1 = action[0]
    next_act_2 = action[1]

    temp_air = forecasts['TDryBul'][step]
    dni = forecasts['HDirNor'][step]
    dhi = forecasts['HDifHor'][step]
    ghi = forecasts['HHorIR'][step]
    w_sp = forecasts['winSpe'][step]

    ac_power = get_total_pv_precal(day_no=solar_info['day_no'],i=solar_info['i'])
    dc_power = 0.95*ac_power

    cur_soc = art_curr_agent_states[0][8]*batt_info['batt_cap']
    next_soc,batt_pow_prov,net_grid_power,pow_sold,other_info = battery_calc(act_02=next_act_2,                                                         
                                                                batt_info = batt_info,
                                                                cur_soc= cur_soc,
                                                                step=600,
                                                                tot_pow=tot_pow,
                                                                dc_power=dc_power)

    
    if suppress==False:
        print ("mean temp hist: {},next_mean_temp: {}".format(mean_temp_hist,next_mean_temp))

    mean_temp_hist = np.insert(mean_temp_hist,0,next_mean_temp)   
    mean_temp_hist = mean_temp_hist[:-1]         
    next_agent_states = np.array([[next_mean_temp,next_hour,next_oa,next_oa_f1,next_sol,next_sol_f1,next_dr_m1,next_dr_m0,next_soc/81]])  
    
    return next_agent_states,mean_temp_hist

def X_pso_2_act_pso(X_pso,steps,dimensions):
  return X_pso.T.reshape(steps,dimensions)

def act_pso_2_X_pso(action_pso,steps,dimensions):
  return np.array(action_pso).T.reshape(dimensions,steps)