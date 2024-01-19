import pandas as pd
import numpy as np 
import math; import random;
import collections; from collections import deque
from c2_surrogate_models_v3 import *
from c9_RL_functions import *
from c5_functions import *
from c7_reward_calc import * 
from c8_variables import * 
from c6_solar_pv import get_total_pv 
from replay_memory import ReplayMemory

import os;  import numpy as np; import pandas as pd 
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from matplotlib import pyplot
from sklearn.datasets import make_regression
import scipy as stats
from scipy.spatial import distance
from scipy.stats import chi2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from matplotlib import pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
import joblib
import tensorflow as tf
import tensorflow
from tensorflow.keras.layers import Dense 
from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import LSTM 
from c9a_art_train_functions import * 
from sac_2 import SAC
import argparse

updates = 0
parser = argparse.ArgumentParser(description='PyTorch Soft Actor-Critic Args')
parser.add_argument('--env-name', default="HalfCheetah-v2",
                    help='Mujoco Gym environment (default: HalfCheetah-v2)')
parser.add_argument('--policy', default="Gaussian",
                    help='Policy Type: Gaussian | Deterministic (default: Gaussian)')
parser.add_argument('--eval', type=bool, default=True,
                    help='Evaluates a policy a policy every 10 episode (default: True)')
parser.add_argument('--gamma', type=float, default=0.9995, metavar='G',
                    help='discount factor for reward (default: 0.99)')
parser.add_argument('--tau', type=float, default=0.005, metavar='G',
                    help='target smoothing coefficient(τ) (default: 0.005)')
parser.add_argument('--lr', type=float, default=0.0001, metavar='G',
                    help='learning rate (default: 0.0003)')
parser.add_argument('--alpha', type=float, default=0.3, metavar='G',
                    help='Temperature parameter α determines the relative importance of the entropy\
                            term against the reward (default: 0.2)')
parser.add_argument('--automatic_entropy_tuning', type=bool, default=False, metavar='G',
                    help='Automaically adjust α (default: False)')
# parser.add_argument('--seed', type=int, default=123456, metavar='N',
#                     help='random seed (default: 123456)')
parser.add_argument('--batch_size', type=int, default=144*2, metavar='N',
                    help='batch size (default: 256)')
parser.add_argument('--num_steps', type=int, default=1000001, metavar='N',
                    help='maximum number of steps (default: 1000000)')
parser.add_argument('--hidden_size', type=int, default=[1000,1600,1000], metavar='N',
                    help='hidden size (default: 256)')
parser.add_argument('--updates_per_step', type=int, default=10, metavar='N',
                    help='model updates per simulator step (default: 1)')
parser.add_argument('--start_steps', type=int, default=10000, metavar='N',
                    help='Steps sampling random actions (default: 10000)')
parser.add_argument('--target_update_interval', type=int, default=5, metavar='N',
                    help='Value target update per no. of updates per step (default: 1)')
parser.add_argument('--replay_size', type=int, default=1000000, metavar='N',
                    help='size of replay buffer (default: 10000000)')
parser.add_argument('--cuda', action="store_true",
                    help='run on CUDA (default: False)')
args = parser.parse_args()

buffer_size,batch_size= 10^5,288*3
delta_sp = 7.5
power_scale = 80000

suppress = True


path_NN ='RL_Data_test/03_LSTM_SAC/02_NN/'
# lstm_name = path_NN+'05_LSTM/lstm_'+str(last_ep)+'.h5'

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

t_sel_keys = np.load('t_sel_keys.npy')
r_sel_keys = np.load('r_sel_keys.npy')  

class Agent_search():
     def __init__(self,batch_size,lr,buffer_size,path_NN):                  
          self.step = 300 
          self.batch_size = batch_size
          self.memory = deque(maxlen=buffer_size)
          self.n_samples = None
          self.KPI_rewards = None 
          self.df = None   
          self.path_NN = path_NN      
          
          self.lower_r_bounds = np.array([[min_temp, 0,min_oa,min_sol,min_dr,min_dr,min_batt,0,0]]) 
          self.upper_r_bounds = np.array([[max_temp,24,max_oa,max_sol,max_dr,max_dr,max_batt,1, 1]])
          self.lower_t_bounds = np.array([[min_temp,min_temp, 0,min_oa,min_sol,0]]) 
          self.upper_t_bounds = np.array([[max_temp,max_temp,24,max_oa,max_sol,1]])

          self.gen_low_bounds = np.array([min_temp, 0,min_oa,min_oa,min_sol,min_sol,0, 0, 0])
          self.gen_upp_bounds = np.array([max_temp,24,max_oa,max_oa,max_sol,max_sol,1, 1, 1])          
          
          self.batt_info = batt_info
          self.DR_time = None
          self.buffer_size = 288*100
          self.full_df = None
          self.pso_dimensions = None
          self.pso_steps = None 

          self.r_model  = get_r_model(lr,len(r_sel_keys),1)
          self.t_model = RandomForestRegressor(n_estimators=1000,criterion="squared_error")
          self.agent_2 = SAC(custom_observation_space.shape[0], custom_action_space, args)

     def init_df(self,steps_forward):
          reward_names = []
          action_names = []
          state_names = []
          actual_action = []
          for step in range(steps_forward):
               action_names.append('a'+str(step+1))
               reward_names.append('r'+str(step+1))
               state_names.append('s'+str(step+1))
               actual_action.append('action_'+str(step+1))
     
          column_names = reward_names + action_names + state_names+actual_action
          
          df = pd.DataFrame(columns=column_names)
          return df,reward_names,action_names
     

     def load_past_dfs(self,path):
          file_names = os.listdir(path+"04_Mem/")
          self.full_df =  pd.DataFrame()
          for i in range(len(file_names)):
               df1 = pd.read_pickle(path+"/04_Mem/"+file_names[i])
               df1 = ret_single_t_df(df1)
               self.full_df = pd.concat([self.full_df,df1])   

     
     def load_dfs(self,df):
          self.full_df = pd.concat([self.full_df,df])   


     def model_selection(self):
          full_t_keys = ['mean_T','mean_T_m1','time','oa_0','oa_1','sol_0','sol_1','a1']
          full_r_keys = ['mean_T_m1','mean_T','time','oa_0','oa_1','sol_0','sol_1','a1','a2','dr_m1','dr_m0','cur_soc']

          X_t =self.full_df[full_t_keys]
          y_t = self.full_df[['delta_t','power']]  

          X_r =self.full_df[full_r_keys]
          y_r = self.full_df[['reward']] 

          t_model = RandomForestRegressor(n_estimators=1000,criterion="squared_error")
          r_model = RandomForestRegressor(n_estimators=1000,criterion="squared_error")              
          
          t_model.fit(X_t, y_t)  
          r_model.fit(X_r, y_r)  

          t_sort = t_model.feature_importances_.argsort()
          r_sort = r_model.feature_importances_.argsort()

          T_value = np.flip(t_model.feature_importances_[t_sort])
          T_value_cum = np.cumsum(T_value,axis=0)
          t_val = len(T_value_cum[T_value_cum<0.95])
          T_sort = np.flip(X_t.columns[t_sort])[0:t_val]
          t_sel_keys = T_sort.tolist()

          R_value = np.flip(r_model.feature_importances_[r_sort])
          R_value_cum = np.cumsum(R_value,axis=0)
          r_val = len(R_value_cum[R_value_cum<0.95])
          R_sort = np.flip(X_r.columns[r_sort])[0:r_val]
          r_sel_keys = R_sort.tolist()

          return t_sel_keys,r_sel_keys
     

     
     def train_surr(self,t_sel_keys,r_sel_keys,epochs):        

          X_t = self.full_df[t_sel_keys]
          y_t = self.full_df[['delta_t','power']]    

          X_r = self.full_df[r_sel_keys]
          y_r = self.full_df[['reward']]          
          
          self.t_model.fit(X_t, y_t)           
          history = self.r_model.fit(X_r,y_r, epochs=epochs, batch_size=self.batch_size,verbose=1)
          # loss = history.history['loss'][0]

     def save_models(self):
          self.r_model.save_weights(self.path_NN+"r_model.h5")
          joblib.dump(self.t_model, self.path_NN+"t_model.joblib")

     def load_models(self):
          self.r_model.load_weights(self.path_NN+"r_model.h5")
          self.append_model_samplet_model = joblib.load(self.path_NN+"t_model.joblib")


     def t_predict(self,t_state):
          return self.t_model.predict(t_state,verbose=0)

     def r_predict(self,r_state):
          return self.r_model.predict(r_state,verbose=0)
           
    
     def form_gen_next_state(self,next_lstm_state_m1,agent_state,action,tot_power,dc_power):          
          cur_oa = agent_state[2]
          for_oa = agent_state[3]
          cur_ghi =agent_state[4]
          for_ghi =agent_state[5]
          cur_soc =agent_state[8]
          prev_sp = 273.15+22.5+action[0]*delta_sp                       

          next_mean_temp = next_lstm_state_m1[0]
          next_hou = next_lstm_state_m1[3]          
          next_cur_oa = cur_oa+self.step/3600*(for_oa-cur_oa)
          next_for_oa = next_cur_oa + (for_oa-cur_oa)
          next_cur_ghi = cur_ghi + self.step/3600*(cur_ghi-for_ghi)
          next_for_ghi = next_cur_ghi + (for_ghi-cur_ghi)          

          DR_time_h = np.array(self.DR_time)/3600

          if (next_hou>= DR_time_h[0])&(next_hou<=DR_time_h[1]):
               next_dr_p0 = 1
          else:
               next_dr_p0 = 0 

          next_dr_p1 = (DR_time_h[0]-next_hou)/16
          if next_dr_p1<0:
               next_dr_p1 = 0    

          ''' Get battery next state'''
          next_soc,curt_pow,net_grid_power = battery_calc(action[1],action[2],self.batt_info,cur_soc,self.step,tot_pow=tot_power,dc_power=dc_power) 
          next_battery_states = np.array([next_soc,curt_pow,net_grid_power])
          ''' Get battery next state'''  

          next_agent_state = np.array([next_mean_temp,next_hou,next_dev_sp,next_cur_oa,next_for_oa,next_cur_ghi,next_for_ghi,next_dr_p1,next_dr_p0,next_soc])
          next_agent_state_n = np.array([(float(x)-self.gen_low_bounds[y])/(self.gen_upp_bounds[y]-self.gen_low_bounds[y]) for x,y in zip(next_agent_state,np.arange(len(next_agent_state)))])
                                    
          return next_agent_state,next_agent_state_n,next_battery_states         


     def store_sample_trajectory(self,state_n,action):
          return None 
     
     def form_curr_df(self,curr_agent_states_n,mean_temp_hist_n):           
          df1 = pd.DataFrame({'states':[curr_agent_states_n[0]],
                                'oa_0':[curr_agent_states_n[0][2]],'oa_1':[curr_agent_states_n[0][3]],
                                'sol_0':[curr_agent_states_n[0][4]],'sol_1':[curr_agent_states_n[0][5]],
                                'mean_T':[curr_agent_states_n[0][0]],'mean_T_m1':[mean_temp_hist_n[1]],
                                'dr_m1':[curr_agent_states_n[0][6]],'dr_m0':[curr_agent_states_n[0][7]],
                                'cur_soc':[curr_agent_states_n[0][8]],'time':[curr_agent_states_n[0][1]],
                                })                
          return df1
     

     def art_form_curr_df(self,curr_agent_states_n):           
          df1 = pd.DataFrame({'states':[curr_agent_states_n[0]],
                                'oa_0':[curr_agent_states_n[0][2]],'oa_1':[curr_agent_states_n[0][3]],
                                'sol_0':[curr_agent_states_n[0][4]],'sol_1':[curr_agent_states_n[0][5]],
                                'mean_T':[curr_agent_states_n[0][0]],'dr_m1':[curr_agent_states_n[0][6]],
                                'dr_m0':[curr_agent_states_n[0][7]],'cur_soc':[curr_agent_states_n[0][8]],
                                'time':[curr_agent_states_n[0][1]] })                
          return df1
    

     def form_curr_r_and_t_state(self,df1,t_sel_keys,r_sel_keys,unprocessed_final_action):

          df1['action'] = [unprocessed_final_action]
          df1['a1'] = [unprocessed_final_action[0]]
          df1['a2'] = [unprocessed_final_action[1]] 

          X_t = df1[t_sel_keys]            
          X_r = df1[r_sel_keys]             
                           
          return X_t, X_r

     def scale_r_state(self,r_state_n):                    
          r_state = r_state_n*(self.upper_r_bounds-self.lower_r_bounds)+self.lower_r_bounds
          return r_state 

     def normalize_r_state(self,r_state): 
          r_state_n = (r_state - self.lower_r_bounds)/(self.upper_r_bounds-self.lower_r_bounds)
          return r_state_n

     def scale_t_state(self,t_state_n):  
          t_state = t_state_n*(self.upper_t_bounds-self.lower_t_bounds)+self.lower_t_bounds
          return t_state 

     def normalize_t_state(self,t_state): 
          t_state_n = (t_state - self.lower_t_bounds)/(self.upper_t_bounds-self.lower_t_bounds)
          return t_state_n      

        
     def gen_trajectory(self,samples,keys,steps_forward,df1,forecasts,mean_temp_hist_n,DR_time,solar_info):
          df,reward_names,column_names = self.init_df(steps_forward=steps_forward)
          t_sel_keys = keys[0]
          r_sel_keys = keys[1]

          for key in forecasts.keys():
               forecasts[key] = np.repeat(forecasts[key],int(3600/300)).tolist()

          mean_temp_hist = mean_temp_hist_n*(max_temp-min_temp)+ min_temp
          mean_temp_hist_fix = mean_temp_hist        
          df_fix = df1
              
          for sample in range(samples):   
               df1 = df_fix
               mean_temp_hist = mean_temp_hist_fix             
               for step in range(steps_forward):
                    action_index = np.random.choice(action_indexes)                    
                    action = self.get_action_from_index(action_index)    
                    # if suppress==False:
                    #      print ("sample: {}; step: {}; df1: {}".format(sample,step,df1))                    
                    t_state,r_state = self.form_curr_r_and_t_state(df1,t_sel_keys,r_sel_keys,action)                                                        
                                 
                    df.loc[sample,'a'+str(step+1)] = action_index  
                    df.loc[sample,'s'+str(step+1)] = df1['states'].iloc[0]
                    df.loc[sample,'r'+str(step+1)] = self.r_model.predict(r_state,verbose=0)[0][0]*(0.75**step)
                    df.loc[sample,'action_'+str(step+1)] = action
                    ''' form next state''' 

                    t_pred =   self.t_model.predict(t_state)[0]                 
                    delta_T = t_pred[0]
                    tot_pow = t_pred[1]*power_scale

                    # print ()
                    # print ("t_state: {}; pred: {}".format(t_state_n,delta_T))
                    # print ()
                    curr_agent_states, mean_temp_hist = self.form_next_agent_state(df1=df1, 
                                                                 tot_pow = tot_pow,                                                                
                                                                 action=action,
                                                                 step=step+1,
                                                                 forecasts=forecasts,
                                                                 delta_T = delta_T,
                                                                 mean_temp_hist=mean_temp_hist,
                                                                 DR_time=DR_time,
                                                                 solar_info=solar_info)  
                    curr_agent_states_n = (curr_agent_states-self.gen_low_bounds)/(self.gen_upp_bounds-self.gen_low_bounds)
                    mean_temp_hist_n = (mean_temp_hist - min_temp)/(max_temp-min_temp)

                    df1 = self.form_curr_df(curr_agent_states_n,mean_temp_hist_n)
                    ''' form next state'''                    
          df["r_sum"] = df[reward_names].sum(axis=1)   
          #df.to_pickle("check_df.pkl")  
          return df 
     
     def gen_trajectory_2(self,samples,keys,steps_forward,df1,forecasts,mean_temp_hist_n,DR_time,solar_info,agent_2,curr_agent_states_n):
          df,reward_names,column_names = self.init_df(steps_forward=steps_forward)
          t_sel_keys = keys[0]
          r_sel_keys = keys[1]
          alpha= 0.2

          for key in forecasts.keys():
               forecasts[key] = np.repeat(forecasts[key],int(3600/300)).tolist()

          mean_temp_hist = mean_temp_hist_n*(max_temp-min_temp)+ min_temp
          mean_temp_hist_fix = mean_temp_hist      
          curr_agent_states_n_fix = curr_agent_states_n    
          df_fix = df1
          suppress=True
              
          for sample in range(samples):   
               print ("sample: {}".format(sample))
               df1 = df_fix
               mean_temp_hist = mean_temp_hist_fix   
               curr_agent_states_n  = curr_agent_states_n_fix            
               for step in range(steps_forward):
                    action_index = np.random.choice(action_indexes)  
                    hours = df1['time'].iloc[0]*24
                    # print ("hours: {}".format(hours))
                    cur_soc_n = df1['cur_soc'].iloc[0]
                    sp = get_sp(hours)[0]
                    # rbc_act = rbc_action_online(hours,DR_time,sp,cur_soc_n)    
                    base_act = agent_2.select_action(state=curr_agent_states_n[0].tolist())

                    action = base_act +np.array([np.random.uniform(alpha,-alpha),np.random.uniform(alpha,-alpha)]) 
                    action = np.clip(action,-1,1)

                    

                    # action = self.get_action_from_index(action_index)    
                                 
                    t_state,r_state = self.form_curr_r_and_t_state(df1,t_sel_keys,r_sel_keys,action)     
                    reward = self.r_model.predict(r_state,verbose=0)[0][0]*(0.95**step)                                                   
                                 
                    df.loc[sample,'a'+str(step+1)] = None 
                    df.loc[sample,'s'+str(step+1)] = np.round(df1['states'].iloc[0][0],4)
                    df.loc[sample,'r'+str(step+1)] = reward
                    df.loc[sample,'action_'+str(step+1)] = np.round(action,2)
                    ''' form next state''' 

                    t_pred =   self.t_model.predict(t_state)[0]                 
                    delta_T = t_pred[0]
                    tot_pow = t_pred[1]*power_scale

                    if suppress==False:
                         print ("sample: {}; step: {}".format(sample,step))  
                         print ("state: {}; reward: {}; action: {}".format(df1['states'].iloc[0],reward,action))
                         print ()    

                    # print ()
                    # print ("t_state: {}; pred: {}".format(t_state_n,delta_T))
                    # print ()
                    next_agent_states, mean_temp_hist = self.form_next_agent_state(df1=df1, 
                                                                 tot_pow = tot_pow,                                                                
                                                                 action=action,
                                                                 step=step+1,
                                                                 forecasts=forecasts,
                                                                 delta_T = delta_T,
                                                                 mean_temp_hist=mean_temp_hist,
                                                                 DR_time=DR_time,
                                                                 solar_info=solar_info)  
                    next_agent_states_n = (next_agent_states-self.gen_low_bounds)/(self.gen_upp_bounds-self.gen_low_bounds)
                    mean_temp_hist_n = (mean_temp_hist - min_temp)/(max_temp-min_temp)
                    curr_agent_states_n = next_agent_states_n

                    df1 = self.form_curr_df(curr_agent_states_n,mean_temp_hist_n)

              
                    ''' form next state'''                    
          df["r_sum"] = df[reward_names].sum(axis=1)   
          #df.to_pickle("check_df.pkl")  
          return df 
     

     def gen_trajectory_3(self,samples,keys,steps_forward,df1,forecasts,mean_temp_hist_n,DR_time,solar_info,agent_2,curr_agent_states_n,art_training):
          df,reward_names,column_names = self.init_df(steps_forward=steps_forward)
          t_sel_keys = keys[0]
          r_sel_keys = keys[1]
          alpha= 0.2
          
          self.memory = ReplayMemory(args.replay_size)
          for key in forecasts.keys():
               forecasts[key] = np.repeat(forecasts[key],int(3600/300)).tolist()

          mean_temp_hist = mean_temp_hist_n*(max_temp-min_temp)+ min_temp
          mean_temp_hist_fix = mean_temp_hist      
          curr_agent_states_n_fix = curr_agent_states_n    
          df_fix = df1
          suppress=True
              
          for sample in range(samples):   
               # print ("sample: {}".format(sample))
               df1 = df_fix
               mean_temp_hist = mean_temp_hist_fix   
               curr_agent_states_n  = curr_agent_states_n_fix     
                      
               for step in range(steps_forward):
                    action_index = np.random.choice(action_indexes)  
                    hours = df1['time'].iloc[0]*24
                    # print ("hours: {}".format(hours))
                    cur_soc_n = df1['cur_soc'].iloc[0]
                    sp = get_sp(hours)[0]
                    # rbc_act = rbc_action_online(hours,DR_time,sp,cur_soc_n)    
                    base_act = agent_2.select_action(state=curr_agent_states_n[0].tolist())


                    exp_action = get_action_from_index(action_index)   
                    beta_1 = 0.0 #np.random.uniform(0.4,0.8)  # for approach 2 and approach 3 this should be zero as exploring fully artificially 
                    
                    action = beta_1* base_act + (1-beta_1)*exp_action #for approach 2 

                    # action = base_act +np.array([np.random.uniform(alpha,-alpha),np.random.uniform(alpha,-alpha)]) 
                    action = np.clip(action,-1,1)

                    

                    # action = self.get_action_from_index(action_index)    
                                 
                    t_state,r_state = self.form_curr_r_and_t_state(df1,t_sel_keys,r_sel_keys,action)     
                    reward = self.r_model.predict(r_state,verbose=0)[0][0]*(1**step)                                                   
                                 
                    df.loc[sample,'a'+str(step+1)] = None 
                    df.loc[sample,'s'+str(step+1)] = np.round(df1['states'].iloc[0][0],4)
                    df.loc[sample,'r'+str(step+1)] = reward
                    df.loc[sample,'action_'+str(step+1)] = np.round(action,2)
                    ''' form next state''' 

                    t_pred =  self.t_model.predict(t_state)[0]                 
                    delta_T = t_pred[0]
                    tot_pow = t_pred[1]*power_scale

                    if suppress==False:
                         print ("sample: {}; step: {}".format(sample,step))  
                         print ("state: {}; reward: {}; action: {}".format(df1['states'].iloc[0],reward,action))
                         print ()    

                    # print ()
                    # print ("t_state: {}; pred: {}".format(t_state_n,delta_T))
                    # print ()
                    next_agent_states, mean_temp_hist = self.form_next_agent_state(df1=df1, 
                                                                 tot_pow = tot_pow,                                                                
                                                                 action=action,
                                                                 step=step+1,
                                                                 forecasts=forecasts,
                                                                 delta_T = delta_T,
                                                                 mean_temp_hist=mean_temp_hist,
                                                                 DR_time=DR_time,
                                                                 solar_info=solar_info)  
                    next_agent_states_n = (next_agent_states-self.gen_low_bounds)/(self.gen_upp_bounds-self.gen_low_bounds)
                    mean_temp_hist_n = (mean_temp_hist - min_temp)/(max_temp-min_temp)

                    self.memory.push(curr_agent_states_n[0],action, reward, next_agent_states_n[0],False)
                    curr_agent_states_n = next_agent_states_n
                    df1 = self.form_curr_df(curr_agent_states_n,mean_temp_hist_n)
                    # print (df1)
                    

          updates = 0 
          batch_size = min(args.batch_size,len(self.memory))
          if art_training == True:
               for e in range(10):             
                    critic_1_loss, critic_2_loss, policy_loss, ent_loss, alpha = agent_2.update_parameters(self.memory, batch_size, updates)
                    updates += 1
                    print ("art training epochs: {}".format(e))
                    print ("art training q_value loss1: {}".format(critic_1_loss))
                    print ("art training q_value loss2: {}".format(critic_2_loss))
                    print ("art training policy loss: {}".format(policy_loss))
                    # print ("ent loss: {}".format(ent_loss))   
                    # print ("alpha: {}".format(alpha))   
                    print ()     

              
          ''' form next state'''                    
          df["r_sum"] = df[reward_names].sum(axis=1)  
          # print (df) 
          #df.to_pickle("check_df.pkl")  
          return df, agent_2

     def  form_next_agent_state(self,df1,tot_pow,action,step,forecasts,mean_temp_hist,delta_T,DR_time,solar_info):
          # print ("t_state_n: {}".format(t_state_n))
          # tot_pow = self.t_model.predict(np.array([t_state_n])) 
          # 
          curr_T = df1['states'].iloc[0][0]*(max_temp-min_temp)+min_temp
          curr_time = df1['time'].iloc[0]*24                
                   
          next_mean_temp =  curr_T + delta_T          
          next_hour = (curr_time+600/3600)%24
          next_oa = forecasts['TDryBul'][step]  
          next_oa_f1 = forecasts['TDryBul'][step+12] 
          next_sol= forecasts['HHorIR'][step]  
          next_sol_f1 = forecasts['HHorIR'][step+12] #implement proper
          DR_time_h = np.array(DR_time)/3600

          # print ("DR_time_h: {}".format(DR_time_h))
          # print ("next_hour: {}".format(next_hour))

          if (next_hour>= DR_time_h[0])&(next_hour<=DR_time_h[1]):
               next_dr_m0 = 1
          else:
               next_dr_m0 = 0 

          dr_signal_time = 4 

          countdown_dr =  DR_time_h[0] - next_hour

          if countdown_dr>dr_signal_time:
            countdown_dr =0 
          elif countdown_dr>0 and countdown_dr<=dr_signal_time:
               countdown_dr = dr_signal_time - countdown_dr
          else:
               countdown_dr = 0
        
          next_dr_m1 = countdown_dr/dr_signal_time
         
          if next_dr_m1>0:
               next_dr_m0 = (DR_time_h[1]-DR_time_h[0])/4

          next_act_1 = action[0]
          next_act_2 = action[1]

          temp_air = forecasts['TDryBul'][step]
          dni = forecasts['HDirNor'][step]
          dhi = forecasts['HDifHor'][step]
          ghi = forecasts['HHorIR'][step]
          w_sp = forecasts['winSpe'][step]

          ac_power = self.get_total_pv_precal(day_no=solar_info['day_no'],i=solar_info['i'])
          dc_power = 0.95*ac_power

          cur_soc = df1['cur_soc'].iloc[0]*batt_info['batt_cap']
          next_soc,batt_pow_prov,net_grid_power,pow_sold,other_info = battery_calc(act_02=next_act_2,                                                         
                                                                      batt_info = batt_info,
                                                                      cur_soc= cur_soc,
                                                                      step=300,
                                                                      tot_pow=tot_pow,
                                                                      dc_power=dc_power)

          
          if suppress==False:
               print ("mean temp hist: {},next_mean_temp: {}".format(mean_temp_hist,next_mean_temp))

          mean_temp_hist = np.insert(mean_temp_hist,0,next_mean_temp)   
          mean_temp_hist = mean_temp_hist[:-1]         
          next_agent_states = np.array([[next_mean_temp,next_hour,next_oa,next_oa_f1,next_sol,next_sol_f1,next_dr_m1,next_dr_m0,next_soc/batt_info['batt_cap']]])  
          
          return next_agent_states,mean_temp_hist
     
     def art_form_next_agent_state(self,df1,tot_pow,action,step,forecasts,mean_temp_hist,delta_T,DR_time,solar_info):
          # print ("t_state_n: {}".format(t_state_n))
          # tot_pow = self.t_model.predict(np.array([t_state_n])) 
          # 
          curr_T = df1['states'].iloc[0][0]*(max_temp-min_temp)+min_temp
          curr_time = df1['time'].iloc[0]*24      
          next_oa = df1['states'].iloc[0][2]*(max_oa-min_oa)+min_oa
                   
          next_mean_temp =  curr_T + delta_T          
          next_hour = (curr_time+600/3600)%24          
          next_oa_f1 = next_oa + np.random.uniform(-0.3,0.3)
          next_sol= df1['time'].iloc[0]  
          next_sol_f1 = next_sol + np.random.uniform(-100,100)
          DR_time_h = np.array(DR_time)

          # print ("DR_time_h: {}".format(DR_time_h))
          # print ("next_hour: {}".format(next_hour))

          if (next_hour>= DR_time_h[0])&(next_hour<=DR_time_h[1]):
               next_dr_m0 = 1
          else:
               next_dr_m0 = 0 

          dr_signal_time = 4 

          countdown_dr =  DR_time_h[0] - next_hour

          if countdown_dr>dr_signal_time:
            countdown_dr =0 
          elif countdown_dr>0 and countdown_dr<=dr_signal_time:
               countdown_dr = dr_signal_time - countdown_dr
          else:
               countdown_dr = 0
        
          next_dr_m1 = countdown_dr/dr_signal_time
         
          if next_dr_m1>0:
               next_dr_m0 = (DR_time_h[1]-DR_time_h[0])/4

          next_act_1 = action[0]
          next_act_2 = action[1]

          temp_air = forecasts['TDryBul'][step]
          dni = forecasts['HDirNor'][step]
          dhi = forecasts['HDifHor'][step]
          ghi = forecasts['HHorIR'][step]
          w_sp = forecasts['winSpe'][step]

          ac_power = self.get_total_pv_precal(day_no=solar_info['day_no'],i=solar_info['i'])
          dc_power = 0.95*ac_power

          cur_soc = df1['cur_soc'].iloc[0]*batt_info['batt_cap']
          next_soc,batt_pow_prov,net_grid_power,pow_sold,other_info = battery_calc(act_02=next_act_2,                                                         
                                                                      batt_info = batt_info,
                                                                      cur_soc= cur_soc,
                                                                      step=300,
                                                                      tot_pow=tot_pow,
                                                                      dc_power=dc_power)

          
          if suppress==False:
               print ("mean temp hist: {},next_mean_temp: {}".format(mean_temp_hist,next_mean_temp))

          mean_temp_hist = np.insert(mean_temp_hist,0,next_mean_temp)   
          mean_temp_hist = mean_temp_hist[:-1]         
          next_agent_states = np.array([[next_mean_temp,next_hour,next_oa,next_oa_f1,next_sol,next_sol_f1,next_dr_m1,next_dr_m0,next_soc/batt_info['batt_cap']]])  
          
          return next_agent_states,mean_temp_hist

     
     def get_action_from_index(self,action_index):
          a1_index= action_id[action_id['action_index']==action_index].a1.item()
          a2_index= action_id[action_id['action_index']==action_index].a2.item()
          act = np.array([a1_guides[a1_index],a2_guides[a2_index]])
          return act

     def find_opt_first_action(self,df):
          first_action_index = df.loc[df[['r_sum']].idxmax()].loc[:,'a1'].values[0]     
          return self.get_action_from_index(action_index=first_action_index)
     
     def find_opt_first_action_2(self,df):
          first_action= df.loc[df[['r_sum']].idxmax()].loc[:,'action_1'].values[0]     
          return first_action

     def load_model_data(self,episodes,path):
          self.t_model.load_data(episodes=episodes,path=path)
          self.r_model.load_data(episodes=episodes,path=path)

     def append_model_sample(self,t_state_n,t_pred,r_state_n,r_pred):
          self.t_model.append_sample(t_state=t_state_n,t_pred=t_pred) 
          self.r_model.append_sample(r_state=r_state_n,r_pred=r_pred) 

     def get_total_pv_precal(self,day_no,i):
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

     def min_states(self,df,steps):
          index = df.loc[df[['r_sum']].idxmin()].index.values[0]
          for i in range(steps-1):    
               action = self.get_action_from_index(action_index=df.loc[index,'a'+str(i+1)])
               state = df.loc[index,'s'+str(i+1)]
               next_state = df.loc[index,'s'+str(i+2)]
               reward = df.loc[index,'r'+str(i+1)]
               # print ("state: {}".format(state))
               # print ("action: {}".format(action))
               # print ("reward: {}".format(reward))
          
          df = df.drop([index])

          return df,state,next_state,action,reward
     
     
     
     def cost(self,df1,t_sel_keys,r_sel_keys,forecasts,action_pso,DR_time,solar_info):

          for key in forecasts.keys():
                         forecasts[key] = np.repeat(forecasts[key],int(3600/300)).tolist()       
  
          cost = 0 
          for step_1 in range(len(action_pso)):
               art_action= action_pso[step_1].tolist()
               t_state,r_state = self.form_curr_r_and_t_state(df1,t_sel_keys,r_sel_keys,art_action)
               art_reward = self.r_model.predict(r_state,verbose=0)[0][0]                                   
               ''' form next state'''      
               pred_t_model = self.t_model.predict(t_state)[0]              
               delta_T = pred_t_model[0]                
               tot_pow_p = pred_t_model[1]*power_scale 
     
               art_next_agent_states, art_mean_temp_hist = form_next_agent_state(art_curr_agent_states=art_curr_agent_states,
                                                            action=art_action,
                                                            step=step_1+1,
                                                            forecasts=forecasts,
                                                            delta_T = delta_T,
                                                            mean_temp_hist=art_mean_temp_hist,
                                                            DR_time=DR_time,
                                                            solar_info=solar_info,
                                                            tot_pow=tot_pow_p)  
    
               art_next_agent_states_n = (art_next_agent_states-gen_low_bounds)/(gen_upp_bounds-gen_low_bounds)
               if suppress==False:                    
                    print ("art_state: {}; delta_T: {}; art_action: {}; art_reward: {}".format(art_curr_agent_states,delta_T,art_action,art_reward))
                    print ()
                    # print ("art_curr_agent_states_n: {}; art_next_agent_states_n {}".format(art_curr_agent_states_n,art_next_agent_states_n))
                    print ();print()
                                   
               art_curr_agent_states_n = art_next_agent_states_n 
               art_curr_agent_states = art_curr_agent_states_n * (gen_upp_bounds-gen_low_bounds) + gen_low_bounds
    
               cost = cost+art_reward

          return cost 
     
     def init_X(self,n_particles):
          action_pso =  init_act_pso(self.pso_dimensions,self.pso_steps)
          X = np.array(action_pso).flatten().reshape(self.pso_dimensions*self.steps,1,)
          # print (action_pso)

          for _ in range(n_particles-1):
               action_pso =  init_act_pso(self.pso_dimensions,self.pso_steps)  
               arr = np.array(action_pso).flatten().reshape(6,1,)
               X = np.column_stack((X, arr))

          return X 
     
     def convert_2_X(self,X_pso):
          return X_pso.reshape(-1,self.pso_dimensions,self.pso_steps)
     
     def find_best_pso_act(self,n_particles,iterations,df1,t_sel_keys,r_sel_keys,forecasts,action_pso,DR_time,solar_info):
          X = self.init_X(n_particles)
          V = np.random.randn(self.pso_dimensions, n_particles) * 0.1
          pbest = X
          pbest_obj = self.cost(df1,t_sel_keys,r_sel_keys,forecasts,action_pso,DR_time,solar_info)
          gbest = pbest[:, pbest_obj.argmin()]
          gbest_obj = pbest_obj.min()

          c1 = c2 = 0.6
          w = 0.5

          for i in range(iterations):
               # One iteration 
               print ("pso_iter: {}".format(i))
               r = np.random.rand(2)
               V = w * V + c1*r[0]*(pbest - X) + c2*r[1]*(gbest.reshape(-1,1)-X)
               X = X + V
               
               obj = self.return_cost_array(X,df1,t_sel_keys,r_sel_keys,forecasts,DR_time,solar_info)
               
               pbest[:, (pbest_obj >= obj)] = X[:, (pbest_obj >= obj)]
               pbest_obj = np.array([pbest_obj, obj]).max(axis=0)
               gbest = pbest[:, pbest_obj.argmin()]
               gbest_obj = pbest_obj.min()          

          return X

     def action_pso(self,sample,X):
          return X.T[sample].reshape(-1,self.pso_dimensions)
     
     def return_cost_array(self,X,df1,t_sel_keys,r_sel_keys,forecasts,DR_time,solar_info):
          cost_l = []
          for sample in range(len(X.T)):
               action_pso = self.action_pso(sample,X)
               cost_l.append(self.cost(df1,t_sel_keys,r_sel_keys,forecasts,action_pso,DR_time,solar_info))

          return np.array(cost_l)


     
     



     
                                     






     


     
