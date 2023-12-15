import gym ; import pandas as pd; import numpy as np 
from variables import * 
from gym import spaces
from utils import * 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt; import matplotlib.ticker as ticker
import joblib
from a1_nn_model import * 


class GymEnv(gym.Env):
     def __init__(self,                 
          df                 = None,
          actions            = ['oveDSet_activate'],
          building_obs       = ['sen_hou','Temp_mean_p0','Temp_mean_m1'],
          forecast_obs       = {'occ': [0],'TDryBul': [0, 4], 'winDir': [0], 'HGloHor': [0, 1]},                                 
          episode_length     = 24*3600,
          n_obs              = False,
          random_start_time  = False,                 
          DR_event           = False,
          DR_time            = [3600 * 14, 3600 * 16],
          dr_power_limit     = 10000,
          start_time         = 0,                
          Ts                 = 600, 
          building_id        = 1,   
          day_no             = None,                           
          dr_opt             = 2,   
          extra_info         = None,              
          KPI_rewards        = {"ener_tot": {"hyper": -1, "power": 1},
                              "tdisc_tot": {"hyper": -1, "power": 1},
                              "idis_tot": {"hyper": 0, "power": 1},
                              "cost_tot": {"hyper": 0, "power": 1},
                              "emis_tot": {"hyper": 0, "power": 1},
                              "power_pen":{"hyper":-1,  "power":1}}):  
          


          super(GymEnv,self).__init__()        
          self.actions                = actions
          self.building_obs           = building_obs   
          self.forecast_obs           = forecast_obs  # keys                
          self.episode_length         = episode_length
          self.random_start_time      = random_start_time
          self.KPI_rewards            = KPI_rewards
          self.n_obs                  = n_obs
          self.DR_event               = DR_event
          self.DR_time                = DR_time
          self.Ts                     = Ts
          self.actions                = actions 
          self.min_max                = min_max 
          self.start_time             = start_time 
          self.df                     = pd.read_csv(df) 
          self.kpi_info               = {key:0 for key in kpi_info_list}

          # self.df                     = pd.read_csv("df.csv")
          self.lower_obs_bounds       = lower_obs_bounds
          self.upper_obs_bounds       = upper_obs_bounds        
          self.kpi_integral_last_step = {key: 0 for key in ['ener_tot', 'tdisc_tot', 'idis_tot', 'cost_tot', 'emis_tot']}
          self.building_y             = []
          self.forecast_y             = []          
          self.info                   = {}
          self.action                 = []
          self.u                      = None
          self.reward                 = None
          self.dr_opt                 = dr_opt
          self.dr_power_limit         = dr_power_limit
          self.day_no                 = day_no  
          self.historian              = pd.DataFrame()  
          self.hist_counter           = 0 
          self.extra_info             = extra_info
          self.flag                   = None 
          self.bad_tuple              = None 
          self.building_id            = building_id 

          self.dr_pos_countdown = None
          self.dr_signal_time = 4
          self.actions = actions 
          # self.t_model = RandomForestRegressor(n_estimators=1000,criterion="squared_error")
          # self.t_model = joblib.load("t_model.joblib")
          self.t_model = get_thermal_nn_model(lr=0.000003,state_size= len(t_model_state_keys),pred_size=2)
          
          self.energy_dict = {}
          self.df['tot_secs'] = self.df['tot_secs'].apply(lambda x: int(x))
          
          #print (dir_location)

          # Avoid surpassing the end of the year during an episode
          self.end_year_margin = self.episode_length                
          self.kpi_tdis = dict()
          self.kpi_ener = dict()

          self.path_NN = "0_Data/Case_"+str(self.building_id)+"/02_NN/"

          lr_lighting = 0.0001; lr_appliances = 0.0002 

          self.lighting_model  = get_light_nn_model(lr_lighting,len(lighting_states_sel),1)
          self.appliances_model  = get_appl_nn_model(lr_appliances,len(appliances_states_sel),1)


          self.lighting_model.load_weights(self.path_NN+"lighting_model.h5")
          self.appliances_model.load_weights(self.path_NN+"appliances_model.h5")
          self.t_model.load_weights(self.path_NN+"t_model.h5")

          # Define gym observation space
          self.observation_space = spaces.Box(low  = np.array(self.lower_obs_bounds),
                                            high = np.array(self.upper_obs_bounds),
                                            dtype= np.float32)

          # Parse minimum and maximum values for actions
          self.lower_act_bounds = []
          self.upper_act_bounds = []
          for act in self.actions:
               self.lower_act_bounds.append(self.min_max[act][0])
               self.upper_act_bounds.append(self.min_max[act][1])

       
          self.action_space = spaces.Box(low  = np.array(self.lower_act_bounds),
                                        high = np.array(self.upper_act_bounds),
                                        dtype= np.float32)
          

          self.current_time = self.start_time
          # print (self.df['tot_secs'].iloc[110:140])
          # print ("current time")
          # print (self.current_time)
                 
          self.occupancy = self.df[self.df['tot_secs']==self.current_time]['Occ'].values[0]          
          

     def reset(self):
          self.current_time = self.start_time
          states = self.form_state(time=self.current_time)             
          return states 
     
     def step(self,action):  
          delta_T = 2     
          full_row = self.df[self.df['tot_secs']==self.current_time] #this is a single row of current 
          # print ("action: {}".format(action))
          T = self.get_current_value('Temp_mean_p0')  
          htg = action[0] * (min_max['u_heat_stp'][1]-min_max['u_heat_stp'][0]) + min_max['u_heat_stp'][0]
          clg = action[1] * (min_max['u_cool_stp'][1]-min_max['u_cool_stp'][0]) + min_max['u_cool_stp'][0]
          T_oa = self.get_current_value('temp_OA')

          # print ("htg check")
          # print (htg,clg)
                           
          htg,clg = training_override(T,htg,clg,T_oa)
          # print ("htg clg after training override: {}".format([htg,clg]))    
          
          htg_n = normalize(value= htg,key='u_heat_stp')
          clg_n = normalize(value= clg,key='u_cool_stp')

          # print ("Normalized actions {},{}".format(htg_n,clg_n))
          
          full_row['u_heat_stp'],full_row['u_cool_stp'] = htg,clg 
          
          
          # print ("full row in step: {}".format(full_row[t_model_state_keys+t_model_pred_sel]))
          hours = full_row['sen_hou'].values[0]
          X_t ,X_t_n = normalize_t_state(full_row)
          X_t_n = np.array([X_t_n]) 
          # print ("X_t_n: {}".format(X_t_n))

          X_light_n = np.array([normalize_lighting_state(full_row)]) 
          X_appliances_n = np.array([normalize_appliance_state(full_row)]) 

          # print ("Input state for X-light: {}".format(X_light_n))
          # print ("Input state for X-appliance: {}".format(X_appliances_n))

          pred_lighting_model = self.lighting_model.predict(X_light_n,verbose=0)               # the min_max power scaling unit is kW 
          pred_appliances_model = self.appliances_model.predict(X_appliances_n,verbose=0)

          lighting_pow =  self.get_current_value('elec_lights')   #pred_lighting_model[0][0]* min_max["elec_lights"][1]
          appliances_pow =  self.get_current_value('appliances_pow')  #pred_appliances_model[0][0] * min_max["appliances_pow"][1]

          pred_t_model= self.t_model.predict(X_t_n,verbose=0)[0]   #this one predicts the deltaT and power consumption 
      
          delta_T = pred_t_model[0]/scale_delta 

          # print ("scaled back delta: {}".format(delta_T))
          
          min_val, max_val = -9,9 #setting limits to the prediction of delta 
          delta_T = np.clip(delta_T,min_val,max_val)

          # print ("predicted t_model outputs: {}, modified deltaT: {}".format(pred_t_model,delta_T))        
          # print ("lighting_pow : {}; appliances_pow: {}".format(lighting_pow,appliances_pow))

          pred_power = max(0,pred_t_model[1])                    
          hvac_pow = (pred_power/scale_hvac* min_max["hvac_dem_tot"][1])
          
          # print ("delta_T : {}; hvac_pow: {}".format(delta_T,hvac_pow))
          tot_pow_p = hvac_pow  + lighting_pow + appliances_pow

          self.energy_dict['hvac_pow'] = hvac_pow 
          self.energy_dict['lighting_pow'] = lighting_pow
          self.energy_dict['appliances_pow'] = appliances_pow

          curr_temp = self.df.loc[self.df['tot_secs'] == self.current_time]['Temp_mean_p0'].values[0]
          
          # print ("curr temp: {}".format(curr_temp))
          
          next_temp = curr_temp   + delta_T  
      
          self.df.loc[self.df['tot_secs'] == self.current_time + self.Ts, 'Temp_mean_p0'] = next_temp
          self.df.loc[self.df['tot_secs'] == self.current_time + self.Ts, 'Temp_mean_m1'] = curr_temp  

          # print ("current time {}, changes to {}".format(self.current_time,self.current_time+ self.Ts ))

          self.current_time = self.current_time+ self.Ts 
          
          occ = full_row['Occ'].values[0]
          self.kpi_info['tdisc_tot'] = calc_thermal_disc(hours = hours,temp = next_temp, occupancy = occ,Ts = self.Ts)
          self.kpi_info['ener_tot'] = tot_pow_p * self.Ts/3600   #kW *hour

          next_states = self.form_state(time=self.current_time)

          done = self.compute_done()
          self.reward = self.compute_reward()
          info = self.get_info() 
          info['Occ'] = self.get_current_value('Occ')
          info['u_heat_stp'],info['u_cool_stp'] = htg,clg 
          info['X_t'] = X_t
          return next_states,self.reward,done,info 
     
     def get_info(self):
          info = {}
          info['flag'] = self.flag 
          return info
     
     def compute_reward(self):
          reward = 0           
          # print (self.kpi_info.keys()) 
          print (self.KPI_rewards)  
          for kpi in self.kpi_info.keys():
               reward = reward + self.KPI_rewards[kpi]["hyper"]*self.kpi_info[kpi]**(self.KPI_rewards[kpi]["power"])
          return reward 
     
     def form_state(self,time):
          states = []; keys = []       
          for building_key in self.building_obs:
               val = self.df[self.df['tot_secs']==time][building_key].values[0]
               states.append(val)
               keys.append(building_key)

          for forecast_key in self.forecast_obs:
               for horizon in self.forecast_obs[forecast_key]:
                    val = self.df[self.df['tot_secs']== time + horizon*self.Ts][forecast_key].values[0]                   
                    states.append(val)
                    keys.append(forecast_key)

          if self.n_obs == True: 
               states = [(x-min_max[key][0])/(min_max[key][1]-min_max[key][0]) for x,key in zip(states,keys)]            

          return states 
     
     def get_current_value(self,key):
          value = self.df[self.df['tot_secs']==self.current_time][key].values[0]
          return value
                    
     def compute_done(self):
          if self.current_time>= self.start_time + self.episode_length: 
               done = True 
          else: 
               done = False 
          return done 
     
     def save_data(self,key_list): 
          for key in key_list: 
               self.historian.loc[self.hist_counter,key] = self.get_current_value(key)
          self.hist_counter +=1 

     
     def save_historian(self,extra_info=False,location=None):          
          extra_info = pd.DataFrame.from_dict(self.extra_info)
          # print ("extra info: {}".format(extra_info))
          # print ("historian: {}".format(self.historian))
          if self.extra_info == False:
               pass
          else:
               print ()
               self.historian = pd.concat([self.historian,extra_info],axis=1) 

          self.historian.to_csv(location)
              
     def plot_data(self,episode,location,day_of_year):   #should be done after save_historian           

          fig = plt.figure(figsize=(25,20), facecolor='white')

          no_of_plots = 6
          label_size = 10
          legend_size = 10
          fontsize = 10
          loc_1 = "upper right"

          x1a = fig.add_subplot(no_of_plots, 2, 1)
          x1b = fig.add_subplot(no_of_plots, 2, 3)
          x1c = fig.add_subplot(no_of_plots, 2, 5)
          # x1d = fig.add_subplot(no_of_plots, 1, 4)

          x2a = fig.add_subplot(no_of_plots, 2, 2)
          x2b = fig.add_subplot(no_of_plots, 2, 4)
          x2c = fig.add_subplot(no_of_plots, 2, 6)

          ''' Temperature Plots '''
          x1a.set_xlim([0,24])
         

          x1a.xaxis.set_major_locator(ticker.MultipleLocator(2))
          x1a.yaxis.set_major_locator(ticker.MultipleLocator(500000))
          # x1a.axvline(x=DR_time[0], color='grey', linestyle='--', linewidth=1, dashes=(2, 2))
          # x1a.axvline(x=DR_time[1], color='grey', linestyle='--',linewidth=1, dashes=(2, 2))
          x1a.set_ylabel('Temperature [C]')
          x1a.grid(which='both', linewidth=0.5, color='white',zorder=3,alpha=0.5)
          x1a.grid(which='major', linewidth=2, color='white',zorder=3,alpha=0.5)

          sequence = ['elec_equip','elec_pump','elec_lights','hvac_dem_tot']
          alpha =  [ 0.4,      0.4,    0.4,   0.4, 0.4]
          colors = ['grey','green','yellow','red']

          x1a.plot([],[],color=colors[0], label=sequence[0], linewidth=2) 
          x1a.plot([],[],color=colors[1], label=sequence[1], linewidth=2) 
          x1a.plot([],[],color=colors[2], label=sequence[2], linewidth=2)
          x1a.plot([],[],color=colors[3], label=sequence[3], linewidth=2)


          x1a.stackplot(df_plot['sen_hou'][:-1], df_plot[sequence[0]][:-1],df_plot[sequence[1]][:-1],df_plot[sequence[2]][:-1],df_plot[sequence[3]][:-1]  ,colors=colors,alpha = alpha)

          x1a.plot(df_plot['sen_hou'][:-1],df_plot['tot_elec'][:-1] , color='k', linewidth=1.5,label='tot_elec')
          x1a.patch.set_alpha(0.4)

          # x1a.step(df['senHouDec_y'], 22.5+df['act_01']*7.5,where="post", color='r',dashes=(4, 1), ls='--',linewidth =1,label='Supervisory Setpoint Action',alpha=0.4)
          # x1a.plot(df['senHouDec_y'],df["meanTemp_y"] - 273.15,label='Mean Temp of all Zones[C]', color="steelblue", linewidth=2*scale,zorder=7)
          x1a.set_ylabel('Total Power [W], Day no: '+str(day_of_year),fontsize=fontsize,fontweight='bold')
          x1a.set_facecolor("gainsboro")
          x1a.tick_params(axis='y', labelsize= label_size)
          x1a.tick_params(axis='x', labelsize= label_size)
          x1a.legend(loc=loc_1,prop={'size': legend_size}).set_zorder(15)



          x1b_s = x1b.twinx()
          x1b_s.plot(df_plot['sen_hou'][:-1],df_plot['Occ_Z1'][:-1] + df_plot['Occ_Z2'][:-1]+df_plot['Occ_Z3'][:-1], color='orange', linewidth=1.5,label='occupancy',alpha = 0.3)


          x1b.xaxis.set_major_locator(ticker.MultipleLocator(2))
          x1b.set_facecolor("gainsboro")
          x1b.step(df_plot['sen_hou'][:-1],df_plot['u_heat_stp'][:-1],where="pre", color='grey', dashes=(2, 2), ls='--', label='Thermal Comfort Bounds',linewidth=2)
          x1b.step(df_plot['sen_hou'][:-1],df_plot['u_cool_stp'][:-1], where="pre", color='grey', dashes=(2, 2), ls='--', linewidth=2)
          x1b.set_ylabel('Temperature [C]')
          x1b.grid(which='both', linewidth=0.5, color='white',zorder=3)
          x1b.grid(which='major', linewidth=2, color='white',zorder=3)
          x1b.plot(df_plot['sen_hou'][:-1],df_plot['Temp_Z2'][:-1] , color='teal', linewidth=2.5,label='temp')
          x1b.patch.set_alpha(0.4)
          x1b.set_xlim([0,24])

          # x1a.step(df['senHouDec_y'], 22.5+df['act_01']*7.5,where="post", color='r',dashes=(4, 1), ls='--',linewidth =1,label='Supervisory Setpoint Action',alpha=0.4)
          # x1a.plot(df['senHouDec_y'],df["meanTemp_y"] - 273.15,label='Mean Temp of all Zones[C]', color="steelblue", linewidth=2*scale,zorder=7)
          x1c.set_ylabel('Temp [C], Day no: '+str(day_of_year ),fontsize=fontsize,fontweight='bold')
          x1c.set_facecolor("gainsboro")
          x1c.tick_params(axis='y', labelsize= label_size)
          x1c.tick_params(axis='x', labelsize= label_size)
          x1c.legend(loc=loc_1,prop={'size': legend_size}).set_zorder(15)
          x1c.set_xlim([0,24])
          x1c.xaxis.set_major_locator(ticker.MultipleLocator(2))
          # x1a.yaxis.set_major_locator(ticker.MultipleLocator())
          # x1a.axvline(x=DR_time[0], color='grey', linestyle='--', linewidth=1, dashes=(2, 2))
          # x1a.axvline(x=DR_time[1], color='grey', linestyle='--',linewidth=1, dashes=(2, 2))
          x1c.set_ylabel('Occupancy')
          x1c.grid(which='both', linewidth=0.5, color='white',zorder=3)
          x1c.grid(which='major', linewidth=2, color='white',zorder=3)
          # x1c.plot(df_plot['sen_hou'][:-1],df_plot['hvac_dem_tot'][:-1],color='r', dashes=(2, 2), ls='--', label='hvac_tot',linewidth=2)
          x1c.plot(df_plot['sen_hou'][:-1],df_plot['Occ_Z1'][:-1] + df_plot['Occ_Z2'][:-1]+df_plot['Occ_Z3'][:-1] , color='orange', linewidth=2.5,label='occ')
          x1c.patch.set_alpha(0.4)
          x1c.set_xlim([0,24])



          sequence = ['hvac_cool','hvac_heat','elec_fans','elec_pump']
          alpha =  [ 0.4,      0.4,    0.4,   0.4, 0.4]
          colors = ['blue','red','green','violet']

          x2a.plot([],[],color=colors[0], label=sequence[0], linewidth=2) 
          x2a.plot([],[],color=colors[1], label=sequence[1], linewidth=2) 
          x2a.plot([],[],color=colors[2], label=sequence[2], linewidth=2)
          x2a.plot([],[],color=colors[3], label=sequence[3], linewidth=2)

          x2a.xaxis.set_major_locator(ticker.MultipleLocator(2))
          x2a.yaxis.set_major_locator(ticker.MultipleLocator(500000))
          x2a.stackplot(df_plot['sen_hou'][:-1], df_plot[sequence[0]][:-1],df_plot[sequence[1]][:-1],df_plot[sequence[2]][:-1],df_plot[sequence[3]][:-1]  ,colors=colors,alpha = alpha)
          x2a.plot(df_plot['sen_hou'][:-1],df_plot['hvac_dem_tot'][:-1] , color='k', linewidth=1.5,label='hvac_dem_tot')
          x2a.patch.set_alpha(0.4)

          # x1a.step(df['senHouDec_y'], 22.5+df['act_01']*7.5,where="post", color='r',dashes=(4, 1), ls='--',linewidth =1,label='Supervisory Setpoint Action',alpha=0.4)
          # x1a.plot(df['senHouDec_y'],df["meanTemp_y"] - 273.15,label='Mean Temp of all Zones[C]', color="steelblue", linewidth=2*scale,zorder=7)
          x2a.set_ylabel('HVAC Power [W], Day no: '+str(day_of_year ),fontsize=fontsize,fontweight='bold')
          x2a.set_facecolor("gainsboro")
          x2a.tick_params(axis='y', labelsize= label_size)
          x2a.tick_params(axis='x', labelsize= label_size)
          x2a.legend(loc=loc_1,prop={'size': legend_size}).set_zorder(15)
          x2a.grid(which='both', linewidth=0.5, color='white',zorder=3,alpha=0.5)
          x2a.grid(which='major', linewidth=2, color='white',zorder=3,alpha=0.5)
          x2a.set_xlim([0,24])


          x2b.xaxis.set_major_locator(ticker.MultipleLocator(2))
          x2b.set_facecolor("gainsboro")

          x2b.set_ylabel('OA Temperature [C]')
          x2b.grid(which='both', linewidth=0.5, color='white',zorder=3)
          x2b.grid(which='major', linewidth=2, color='white',zorder=3)
          x2b.plot(df_plot['sen_hou'][:-1],df_plot['OA_Temp'][:-1] , color='orange', linewidth=1.5,label='temp')
          x2b.patch.set_alpha(0.4)
          x2b.set_xlim([0,24])




          x2c.xaxis.set_major_locator(ticker.MultipleLocator(2))
          # x2c.yaxis.set_major_locator(ticker.MultipleLocator(500000))
          # x2c.stackplot(df_plot['sen_hou'][:-1], df_plot[sequence[0]][:-1],df_plot[sequence[1]][:-1],df_plot[sequence[2]][:-1],df_plot[sequence[3]][:-1]  ,colors=colors,alpha = alpha)
          x2c.plot(df_plot['sen_hou'][:-1],df_plot['chiller_1_cop'][:-1] , color='r', linewidth=1.5,label='chiller_1_cop')
          x2c.plot(df_plot['sen_hou'][:-1],df_plot['chiller_2_cop'][:-1] , color='g', linewidth=1.5,label='chiller_2_cop')
          x2c.plot(df_plot['sen_hou'][:-1],df_plot['chiller_3_cop'][:-1] , color='b', linewidth=1.5,label='chiller_3_cop')
          x2c.patch.set_alpha(0.4)

          # x1a.step(df['senHouDec_y'], 22.5+df['act_01']*7.5,where="post", color='r',dashes=(4, 1), ls='--',linewidth =1,label='Supervisory Setpoint Action',alpha=0.4)
          # x1a.plot(df['senHouDec_y'],df["meanTemp_y"] - 273.15,label='Mean Temp of all Zones[C]', color="steelblue", linewidth=2*scale,zorder=7)
          x2c.set_ylabel('HVAC Power [W], Day no: '+str(day_of_year ),fontsize=fontsize,fontweight='bold')
          x2c.set_facecolor("gainsboro")
          x2c.tick_params(axis='y', labelsize= label_size)
          x2c.tick_params(axis='x', labelsize= label_size)
          x2c.legend(loc=loc_1,prop={'size': legend_size}).set_zorder(15)
          x2c.grid(which='both', linewidth=0.5, color='white',zorder=3,alpha=0.5)
          x2c.grid(which='major', linewidth=2, color='white',zorder=3,alpha=0.5)
          x2c.set_xlim([0,24])

          x2c.xaxis.set_major_locator(ticker.MultipleLocator(2))
          x2c.set_facecolor("gainsboro")

          x2c.set_ylabel('Chiller COP [C]')
          x2c.grid(which='both', linewidth=0.5, color='white',zorder=3)
          x2c.grid(which='major', linewidth=2, color='white',zorder=3)
          x2c.patch.set_alpha(0.4)
          x2c.set_xlim([0,24])



          fig.savefig('1_Figures/power_plot.jpg', dpi=400)
          fig.show()
          
     
     




