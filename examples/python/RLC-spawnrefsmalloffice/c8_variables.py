import numpy as np 
import gym
from gym import spaces



'''KPI Initializer'''
kpi_list = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']
KPI_hist = {key: [] for key in kpi_list}
KPI_hist['episodes'] = []; KPI_hist['scores'] = []
KPI_hist['total_cost'] = []; KPI_hist['energy_total_cost'] = []; KPI_hist['tdisc_total_cost'] = []
KPI_hist['energy_sold_total_cost'] = []; KPI_hist['ppen_total_cost'] = []
KPI_hist['day_no'] = []; KPI_hist['DR_start_time'] = []; KPI_hist['DR_end_time'] = []; KPI_hist['DR_duration'] = []
'''KPI Initializer'''

'''Battery Initializer'''
batt_cap = 13.5 #kWh
cha_eff,dis_eff= 0.95,0.95
dis_cont_pow,cha_cont_pow  = 5.8,7 #kW,kVA
no_of_batteries = 6
batt_info = {'batt_cap':batt_cap*no_of_batteries,'cha_eff':cha_eff,
               'cha_cont_pow': cha_cont_pow*no_of_batteries,'dis_eff':dis_eff,
               'dis_cont_pow':dis_cont_pow*no_of_batteries}
'''Battery Initializer'''

price = {'energy': 0.1279, 't_disc': 0.8, 'dr_price': 7.89 }

score_list = list(); extra_info = dict()
extra_info_lstm = dict()

actions = ['PSZACcontroller_oveHeaStpCor_u','PSZACcontroller_oveHeaStpPer1_u',
           'PSZACcontroller_oveHeaStpPer2_u','PSZACcontroller_oveHeaStpPer3_u',
           'PSZACcontroller_oveHeaStpPer4_u','PSZACcontroller_oveDamCor_u','PSZACcontroller_oveDamP1_u',
           'PSZACcontroller_oveDamP2_u','PSZACcontroller_oveDamP3_u','PSZACcontroller_oveDamP4_u']

kpi_zones = ["0","1","2","3","4"]
building_obs = ['senTemRoom_y','senTemRoom1_y','senTemRoom2_y','senTemRoom3_y','senTemRoom4_y','senHouDec_y']
forecast_obs = {'TDryBul': [0,1],'HHorIR':[0,1]}
dr_obs = [-1,0]

min_oa, max_oa = -20,15
min_sol,max_sol = 0, 1000
min_dr, max_dr = 0,1
min_batt,max_batt = 0,1


min_temp, max_temp = 273.15+18, 273.15+36

lower_obs_bounds = np.array([min_temp,min_temp,min_temp,min_temp,min_temp, 0,min_oa,min_oa,min_sol,min_sol,min_dr,min_dr])
upper_obs_bounds = np.array([max_temp,max_temp,max_temp,max_temp,max_temp,24,max_oa,max_oa,max_sol,max_sol,max_dr,max_dr])

agent_lower_obs_bounds = np.array([min_temp, 0,min_oa,min_oa,min_sol,min_sol, min_dr, min_dr, min_batt])
agent_upper_obs_bounds = np.array([max_temp,24,max_oa,max_oa,max_sol,max_sol, max_dr, max_dr, max_batt])

starting_temp = 18 
step = 300

train_days = [1,2,3,5,6,8,9,10,11,12,16,17,18,19,20,23,24,25,26,27,29,30,32,33,34,36,37,38,39,41,43,44,45,47,48]
# test_days = [4,13,15,22,31,40,46]
test_days = [7,14,28,22,31,40,46]
test_dr_rand_start = np.array([16.2,14.8,15.4,16.0,17.2,15.2,15.8])
dr_dur = np.array([3.2,2.5,3.6,2.8,3.2,3.4,3])

test_dr_rand_end = dr_dur + test_dr_rand_start 

# test_dr_rand_end = np.array([19.04,16.90,17.44,18.88,19.79,17.95,18.69])


sac_act_lower_bnds = [-1,-1]; sac_act_upper_bnds = [1,1]
sac_obs_lower_bnds = [0,0,0,0,0,0,0,0,0]; sac_obs_upper_bnds = [1,1,1,1,1,1,1,1,1]
    
custom_observation_space = spaces.Box(low = np.array(sac_obs_lower_bnds),
                                       high = np.array(sac_obs_upper_bnds),
                                       dtype= np.float32) 
custom_action_space = spaces.Box(low  = np.array(sac_act_lower_bnds),
                                       high = np.array(sac_act_upper_bnds),
                                       dtype= np.float32) 

index = [x for x in range(len(sac_obs_lower_bnds))]

power_scale = 80000
