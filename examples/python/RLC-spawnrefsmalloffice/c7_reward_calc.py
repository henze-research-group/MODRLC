import numpy as np; import pandas as pd
from c9_RL_functions import *

def calc_reward_function(sen_hou,DR_time,next_temp,individual_rewards,extra_info,i):  
    
     occupancy = get_occupancy(sen_hou)     
     sp = get_sp(sen_hou)  ;    ''' Returns temperature in K '''
     temp_dev_ls = list()
     energy_ls = list()
     step = 300 
     

     # print ("hour: {}".format(sen_hou))     
     # print ("extra info price: {}".format(extra_info['price']))     

     # if (sen_hou >= (np.array(DR_time)/3600)[0]) & (sen_hou< (np.array(DR_time)/3600)[1]):
     #      # print("First Condition")
     #      w = [-10, -10, -5, 0]
     #      dr_power_limit = 20000          
     # else:
     #      if sen_hou<5.5 or sen_hou >22:
     #           w = [-100, -10, 0, 0]
     #           dr_power_limit = 150000
     #      else:
     #           # print("Second Condition")
     #           w = [-5, -10, 0, 0]
     #           dr_power_limit = 100000

     if (sen_hou >= (np.array(DR_time)/3600)[0]) & (sen_hou< (np.array(DR_time)/3600)[1]):
          # print("First Condition")
          w = [-1, -1, -1, 0]
          dr_power_limit = 20000          
     else:
          if sen_hou<5.5 or sen_hou >22:
               w = [-1, -1, 0, 0]
               dr_power_limit = 150000
          else:
               # print("Second Condition")
               w = [-1, -1, 0, 0]
               dr_power_limit = 100000

          
     price = extra_info['price'][i]
     net_grid_power = extra_info['net_grid_power'][i]
     net_grid_energy = extra_info['net_grid_energy'][i]
     pow_sold = extra_info['pow_sold'][i]
     t_disc = individual_rewards['Thermal_Discomfort']

     

     energy_sold = pow_sold * step/3600 

     
     # curt_energy = curt_pow/1000*step/3600
     # print ("curt energy: {}".format(curt_energy))
     ppen = (max(0,net_grid_power-dr_power_limit))/1000

     KPI_rewards = {
     "ener_tot": {"hyper": price['energy'] * w[0], "power": 1},
     "tdis_tot": {"hyper": price['t_disc'] * w[1] * occupancy, "power": 1},
     "idis_tot": {"hyper": 0, "power": 1},
     "cost_tot": {"hyper": 0, "power": 1},
     "emis_tot": {"hyper": 0, "power": 1},
     "power_pen":{"hyper": price['dr_price'] * w[2], "power": 1},
     "energy_sold": {"hyper": price['energy']*w[3],"power":1}}         
     

     # for pow in power_used:
     #      energy_ls.append(pow*step/3600)
          
     for temp in next_temp:          
          if (temp<= sp[1])&(temp>=sp[0]):
               temp_dev_ls.append(0)               
          elif (temp>= sp[1]):
               temp_dev_ls.append((temp - sp[1])* step/3600)
          else:
               temp_dev_ls.append((sp[0] -temp)* step/3600)
     

     energy_cost = price['energy'] * net_grid_energy/1000
     tdisc_cost = price['t_disc'] * t_disc *occupancy
     ppen_cost = price['dr_price'] * ppen
     energy_sold_cost = price['energy'] * energy_sold/1000

     # print ("Energy cost: {}; T_disc cost: {}; DR_price: {}".format(energy_cost,tdisc_cost,ppen_cost))     

     cost = energy_cost+tdisc_cost+ppen_cost-energy_sold_cost

     # print ("i: {}".format(i))
     # print ("t_disc: {}; net_grid_energy: {}; pow_sold: {}; energy_sold: {}".format(t_disc,net_grid_energy,pow_sold,energy_sold))

     # print ("Net Grid {}".format(net_grid_power))
     r_tdisc = KPI_rewards['tdis_tot']["hyper"]*t_disc**(KPI_rewards['tdis_tot']["power"])
     r_energy = KPI_rewards['ener_tot']["hyper"]*(net_grid_energy/1000)**(KPI_rewards['ener_tot']["power"])     
     r_ppen = KPI_rewards['power_pen']["hyper"]*ppen**(KPI_rewards['power_pen']["power"])
     r_energy_sold = KPI_rewards['energy_sold']["hyper"]*(energy_sold/1000)**(KPI_rewards['energy_sold']["power"])

     print ("r_t_disc: {}; r_energy: {}; r_ppen: {}; r_energy_sold: {}".format(r_tdisc, r_energy, r_ppen, r_energy_sold))    
     

     mod_reward=dict()
     mod_reward['r_tdisc'] = r_tdisc
     mod_reward['r_energy'] = r_energy
     mod_reward['r_ppen'] = r_ppen
     mod_reward['r_energy_sold'] = r_energy_sold      

     single_reward=dict()
     single_reward['cost_tdisc'] = tdisc_cost
     single_reward['cost_energy'] = energy_cost
     single_reward['cost_ppen'] = ppen_cost
     single_reward['cost_energy_sold'] = energy_sold_cost    

     reward = r_tdisc+r_energy+r_ppen + r_energy_sold
     
     return reward, cost, energy_cost, tdisc_cost, ppen_cost,energy_sold_cost, mod_reward,single_reward

     
     

     

