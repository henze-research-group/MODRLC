
import numpy as np ; import pandas as pd 
from gym import spaces 
import argparse

building_id = 1
case_id = "d"

if case_id == "d" or case_id == "c":
    batt = True 
else:
    batt = False

path = '0_Data/Case_'+str(building_id)+str(case_id)+'/' 
path_NN = path + '02_NN/'

reward_scale = 10/55
# reward_scale = 1 #1000/19.5

min_max = {}

min_max['sen_hou'] = [0,24]
min_max['temp_OA'] = [-20,40]
min_max['rh_OA'] = [0,100]
min_max['Temp_mean_p0'] = [15,30]; min_max['Temp_mean_m1'] = [15,30]
min_max['sen_hou'] = [0,24]
min_max['hir_sol'] = [0,700] 

if building_id == 1: 
    data = '0_Data/Case_1/comb_data.csv'
    min_max["hvac_dem_tot"] = [0,6020] #1  #kW 
    min_max['appliances_pow'] = [0,42] #1 #kW
    min_max['elec_lights'] = [0,70]   #1 #kW
    min_max['Occ'] = [0,3300]
    min_max['batt_cap'] = [0,6000] 
    min_max['rtp'] = [0.05,0.3]
    min_max['soc'] = [0,1]
    scale_delta, scale_hvac = 200 , 200
elif building_id == 6:
    data = '0_Data/Case_6/comb_data.csv'
    min_max["hvac_dem_tot"] = [0,1620] #6  #kW 
    min_max['appliances_pow'] = [0,160] #6 #kW
    min_max['elec_lights'] = [0,190]   #6 #kW
    min_max['Occ'] = [0,250]
    scale_delta, scale_hvac = 600 , 200
      

min_max['u_heat_stp'] = [15,25] 
min_max['u_cool_stp'] = [20,30] 
min_max['delta_T'] = [0,1] 
min_max['Stp_n'] = [0,1] 
min_max['mode'] = [0,1] 

# lighting and appliances follow a random scale where the pred values are limited between 0-10
min_max['elec_equip'] = [0,35]    #kW

lower_obs_bounds = [min_max['sen_hou'][0],min_max['Temp_mean_p0'][0],min_max['Temp_mean_m1'][0],min_max['temp_OA'][0],min_max['Occ'][0]] 
upper_obs_bounds = [min_max['sen_hou'][1],min_max['Temp_mean_p0'][1],min_max['Temp_mean_m1'][1],min_max['temp_OA'][1],min_max['Occ'][1]] 

additional_variables = ['rh_OA'] 

full_batt_cap = 6000 # kWH


train_days = list(range(140,270)) 
# test_days = [4, 17, 23, 55, 78, 85]
test_days = [160,252,190,230,203,273,271]

# looping list of numbers to remove
for n in test_days:
    # taking 1 number found in the list
    # remove it from the list
    while n in train_days:
        train_days.remove(n)

# exclude_days = [231,224,259,140,266,175]

# for n in exclude_days:
#     # taking 1 number found in the list
#     # remove it from the list
#     while n in train_days:
#         train_days.remove(n)

train_days = [num for num in train_days if num % 7 != 0]


t_model_pred_sel =  ['delta_T','hvac_dem_tot']
t_model_state_keys = ['sen_hou','Temp_mean_p0','Temp_mean_m1','temp_OA','rh_OA','Occ','hir_sol','u_heat_stp','u_cool_stp']



kpi_info_list = ['ener_tot', 'tdisc_tot']
KPI_hist = {key: [] for key in kpi_info_list}
KPI_hist['episodes'] = []; KPI_hist['scores'] = []
KPI_hist['day_no'] = [] 
KPI_hist['total_cost'] = []; KPI_hist['energy_total_cost'] = []; KPI_hist['tdisc_total_cost'] = []
KPI_hist['day_no'] = []; KPI_hist['DR_start_time'] = []; KPI_hist['DR_end_time'] = []; KPI_hist['DR_duration'] = []

if batt == True:
    KPI_hist['ener_sold_cost'] = []
    KPI_hist['ev_penalt_cost'] = []



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
parser.add_argument('--tau', type=float, default=0.005, metavar='G',
                    help='target smoothing coefficient(τ) (default: 0.005)')
parser.add_argument('--lr', type=float, default=0.01, metavar='G',
                    help='learning rate (default: 0.0003)')
parser.add_argument('--alpha', type=float, default=0.3, metavar='G',
                    help='Temperature parameter α determines the relative importance of the entropy\
                            term against the reward (default: 0.2)')
parser.add_argument('--automatic_entropy_tuning', type=bool, default=False, metavar='G',
                    help='Automaically adjust α (default: False)')
# parser.add_argument('--seed', type=int, default=123456, metavar='N',
#                     help='random seed (default: 123456)')
parser.add_argument('--batch_size', type=int, default=144*15, metavar='N',
                    help='batch size (default: 256)')
parser.add_argument('--num_steps', type=int, default=1000001, metavar='N',
                    help='maximum number of steps (default: 1000000)')
parser.add_argument('--hidden_size', type=int, default=[1000,1600,1000], metavar='N',
                    help='hidden size (default: 256)')
parser.add_argument('--updates_per_step', type=int, default=1, metavar='N',
                    help='model updates per simulator step (default: 1)')
parser.add_argument('--start_steps', type=int, default=10000, metavar='N',
                    help='Steps sampling random actions (default: 10000)')
parser.add_argument('--target_update_interval', type=int, default=1, metavar='N',
                    help='Value target update per no. of updates per step (default: 1)')
parser.add_argument('--replay_size', type=int, default=144*3000, metavar='N',
                    help='size of replay buffer (default: 10000000)')
parser.add_argument('--cuda', action="store_true",
                    help='run on CUDA (default: False)')
args = parser.parse_args()


t_model_state_keys = ['Temp_mean_p0','Temp_mean_m1','Occ','temp_OA','rh_OA','hir_sol','u_heat_stp','u_cool_stp']
t_model_pred_sel =  ['delta_T','hvac_dem_tot']

lighting_states_sel = ['Temp_mean_p0','sen_hou','temp_OA','hir_sol','Occ']
lighting_preds_sel = ['elec_lights']

appliances_states_sel = ['Temp_mean_p0','sen_hou','temp_OA','Occ']
appliances_preds_sel = ['appliances_pow']




htg_l, clg_l, time_l = [],[],[]
df= pd.read_csv("2_EnergyPlus/02_scheduled_stp.csv")

stp_df = pd.DataFrame(columns=['htg','clg','sen_hou'])

def change_to_senhou(x):
     if x[0]=='24':
          x[0] = 0
     return float(x[0]) + float(x[1])/60 

def round_down_to_half(n):
    return int(2 * n) / 2

for i in range(len(df)):        
    htg = df['htg'].iloc[i]    
    clg = df['clg'].iloc[i]
    time = df['time'].iloc[i]
    htg_l.append(htg)
    clg_l.append(clg)
    time_l.append(change_to_senhou(time.split(":")))
 

stp_df['htg'] = htg_l 
stp_df['clg'] = clg_l 
stp_df['sen_hou'] = time_l 

delta_T = 2  
tdisc_price =  0.8
price_unmet_ev = 0.5 # $/kWh

'''Battery Initializer'''
batt_cap = 13.5 #kWh
cha_eff,dis_eff= 0.95,0.95
dis_cont_pow,cha_cont_pow  = 5.8,7 #kW,kVA
no_of_batteries = 6
batt_info = {'batt_cap':batt_cap*no_of_batteries,'cha_eff':cha_eff,
               'cha_cont_pow': cha_cont_pow*no_of_batteries,'dis_eff':dis_eff,
               'dis_cont_pow':dis_cont_pow*no_of_batteries}
'''Battery Initializer'''


no_of_occ = 3300
percentage = 0.05

ev_owners = int(no_of_occ*percentage)

ev_data = pd.DataFrame(columns=['owner_no','capacity','start_time','end_time','start_soc','end_demand'])
numbers = [20, 30, 40, 70, 100,120]
probabilities = [0.25, 0.35, 0.25, 0.10,0.03,0.02]

start_list =      [   6, 6.5, 7.0,7.5, 8.0, 8.5,    9,  9.5,   10,   11,   12, 13,   14]
prob_start_list = [0.03,0.04,0.04,0.2, 0.4, 0.1, 0.05, 0.04, 0.035, 0.025, 0.02,0.01,0.01] 

end_list =      [  13, 13.5, 14, 14.5,   15, 15.5,   16, 16.5,   17, 17.5, 18, 18.5, 19.0, 19.5, 20, 20.5,  21, 21.5, 22, 23, 24]
prob_end_list = [ 0.5,  1.5,  1,    2,  3, 5,  6,  6, 20, 20,  12,   12,  4,  2.5,   1.25,   1, 1,  0.5, 0.5, 0.25,0]
prob_end_list = [x/100 for x in prob_end_list]

if case_id=="d" or case_id=="c" :
    for owner in range(ev_owners):
        cap = np.random.choice(numbers,p=probabilities)
        new_row = {'owner_no':owner, 'capacity':cap,
                'start_time':np.random.choice(start_list,p=prob_start_list),
                'end_time':np.random.choice(end_list,p=prob_end_list),
                'start_soc': np.random.uniform(low=0.05,high=0.40)*cap,
                'end_demand': np.random.uniform(low=0.95,high=0.100)*cap
                }     
        # print (new_row)
        ev_data = pd.concat([ev_data, pd.DataFrame([new_row])], ignore_index=True)

    ev_data['discharge'] = ev_data['capacity']/5  
    ev_data['charge'] = ev_data['capacity']/3  
    times = np.arange(0, 24.5, 0.5).tolist()
    capacity_per_time = {time: ev_data.loc[(ev_data['start_time'] < time) & (ev_data['end_time'] >= time), 'capacity'].sum() for time in times}
    ev_data.to_csv("0_Data/Case_1c/ev_data.csv")

# print (ev_data)
