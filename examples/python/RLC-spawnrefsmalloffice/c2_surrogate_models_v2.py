"""
This module manages the simulation of SOM3 in BOPTEST. It initializes,
steps and computes controls for the HVAC system.
The testcase docker container must be running before launching this
script.
"""

# GENERAL PACKAGE IMPORT
# ----------------------

import tensorflow as tf 
from tensorflow.keras.layers import Dense 
from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import LSTM 
import numpy as np; import pandas as pd ;import matplotlib.pyplot as plt
from tensorflow.keras import optimizers
from collections import deque
import numpy as np;import pandas as pd; import os 
from collections import OrderedDict
import math; import random; from statistics import mean
from c5_functions import mahalanobis, outlier_clearing


class temperature_model():
     def __init__(self,state_size,pred_size,batch_size,buffer_size,lr):
          self.state_size = state_size
          self.pred_size = pred_size
          self.learning_rate = lr
          self.batch_size = batch_size
          self.memory = deque(maxlen=buffer_size)
          self.model =  self.build_model()
          self.learning_rate = lr

     def build_model(self):
          model = Sequential()
          model.add(LSTM(units=100,batch_input_shape=(None,self.state_size,1),return_sequences=True))    
          model.add(LSTM(units=100,return_sequences=False))             
          model.add(Dense(250, activation="tanh", kernel_initializer='he_uniform'))          
          model.add(Dense(200, activation="linear", kernel_initializer='he_uniform'))
          model.add(Dense(self.pred_size, activation="linear", kernel_initializer='he_uniform'))
          model.summary()
          model.compile(loss='mse',optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate, beta_1=0.9, beta_2=0.999, epsilon=1e-07))
          return model

     def append_sample(self,t_state,t_pred):
        self.memory.append((t_state,t_pred))

     def train_model(self,training_epochs):
          print ("t model memory size check: {}".format(len(self.memory)))
          batch_size = min(self.batch_size,len(self.memory))

          # print ("Memory: {}".format(self.memory))
          mini_batch = random.sample(self.memory,batch_size)
          
          states,preds = [],[]
          for state,pred in mini_batch:  
               # print ("state {}".format(state))
               # print ("pred {}".format(pred)) 
               states.append(state)
               preds.append(pred)

          # history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=1)
          history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=1)
          loss = history.history['loss'][0]
          return loss

     def predict(self,input_state):
          return self.model.predict(input_state,verbose=0)

     def model_save_weights(self,name):
          self.model.save_weights(name)

     def model_load_weights(self,name):
          self.model.load_weights(name)

     def fit(self,states,preds,training_epochs):
          history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=1)
          loss = history.history['loss'][0]
          return loss
     
     def separate_t_state(self,x):
          return x[0]

     def separate_r_state(self,x):
          return x[1]
     
     def form_curr_r_and_t_state(self,curr_agent_states_n,mean_temp_hist_n,action):           
          mean_temp_n = curr_agent_states_n[0]
          mean_temp_n_m2 = mean_temp_hist_n[1]
          hour_n = curr_agent_states_n[1]
          oa_n = curr_agent_states_n[2]   
          sol_n= curr_agent_states_n[4]   
          dr_m1 = curr_agent_states_n[6]          
          dr_m0 = curr_agent_states_n[7]         
          soc_n = curr_agent_states_n[8]          
          
          act_1 = action[0]
          act_2 = action[1]

          r_state_n = np.array([[mean_temp_n,hour_n,oa_n,sol_n,dr_m1,dr_m0,soc_n,act_1,act_2]])
          t_state_n = np.array([[mean_temp_n_m2,mean_temp_n,hour_n,oa_n,sol_n,act_1]]) 

          # t_state = scale_t_state(t_state_n)
          # r_state = scale_r_state(r_state_n)    
    
          return [t_state_n, r_state_n]
     
     def mean_hist(self,x1,x2):
          return [x1[0],x2[0]]
     
     def pre_process(self,df1):
          df1["states_prev"] = df1['states'].shift(1)
          df1 =df1[1:]
          df1["mean_hist"] = df1.apply(lambda x: self.mean_hist(x.states, x.states_prev), axis=1)
          df1["t_r_state"] = df1.apply(lambda x: self.form_curr_r_and_t_state(x.states,x.mean_hist,x.action), axis=1)
          df1['t_state_v1'] = df1.apply(lambda x: self.separate_t_state(x.t_r_state), axis=1)
          df1['r_state_v1'] = df1.apply(lambda x: self.separate_r_state(x.t_r_state), axis=1)
          return df1 

     def load_data(self,episodes,path):
          file_names = os.listdir(path+'04_Mem/')
          df = pd.DataFrame()
          for file_name in file_names[0:episodes]:
               print ("loading file for t model: {}".format(file_name))
               df1 = pd.read_pickle(path+'/04_Mem/'+str(file_name))
               df1 = self.pre_process(df1)
               df = pd.concat([df,df1])

          df = outlier_clearing(df)

          for i in range(len(df)):
               t_state = df.iloc[i]['t_state_v1']
               t_pred = df.iloc[i]['t_pred']               
               self.append_sample(t_state=t_state,t_pred=t_pred)
          

class reward_model():
     def __init__(self,state_size,pred_size,batch_size,buffer_size,lr):
          self.state_size = state_size
          self.pred_size = pred_size
          self.learning_rate = 0.00001
          self.batch_size = batch_size
          self.memory = deque(maxlen=buffer_size)
          self.model =  self.build_model()
          self.learning_rate = lr

     def build_model(self):
          model = Sequential()
          model.add(Dense(300,input_dim=self.state_size,activation="tanh",kernel_initializer = 'he_uniform'))                
          model.add(Dense(450, activation="tanh", kernel_initializer='he_uniform'))          
          model.add(Dense(300, activation="linear", kernel_initializer='he_uniform'))
          model.add(Dense(self.pred_size, activation="linear", kernel_initializer='he_uniform'))
          model.summary()
          model.compile(loss='mse',optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate, beta_1=0.9, beta_2=0.999, epsilon=1e-07))
          return model

     def append_sample(self,r_state,r_pred):
        self.memory.append((r_state,r_pred))

     def train_model(self,training_epochs):
          print ("r model memory size check: {}".format(len(self.memory)))
          batch_size = min(self.batch_size,len(self.memory))

          # print ("Memory: {}".format(self.memory))
          mini_batch = random.sample(self.memory,batch_size)

          # print ("mini-batch : {}".format(mini_batch))

          states,preds = [],[]
          for state,pred in mini_batch:  
               # print ("state {}".format(state))
               # print ("pred {}".format(pred)) 
               states.append(state)
               preds.append(pred)

          # history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=1)
          history = self.model.fit(np.array([states]),np.array(preds),epochs=training_epochs,verbose=1)
          loss = history.history['loss'][0]
          return loss
     
     def separate_t_state(self,x):
          return x[0]

     def separate_r_state(self,x):
          return x[1]
     
     def mean_hist(self,x1,x2):
          return [x1[0],x2[0]]
     
     def pre_process(self,df1):
          df1["states_prev"] = df1['states'].shift(1)
          df1 =df1[1:]
          print ("check 1")
          print (df1.columns)
          df1["mean_hist"] = df1.apply(lambda x: self.mean_hist(x.states, x.states_prev), axis=1)
          df1["t_r_state"] = df1.apply(lambda x: self.form_curr_r_and_t_state(x.states,x.mean_hist,x.action), axis=1)
          df1['t_state_v1'] = df1.apply(lambda x: self.separate_t_state(x.t_r_state), axis=1)
          df1['r_state_v1'] = df1.apply(lambda x: self.separate_r_state(x.t_r_state), axis=1)
          return df1 

     def predict(self,input_state):
          return self.model.predict(input_state,verbose=0)
     
     def fit(self,states,preds,training_epochs):
          history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=1)
          loss = history.history['loss'][0]
          return loss    
              
     def form_curr_r_and_t_state(self,curr_agent_states_n,mean_temp_hist_n,action):           
          mean_temp_n = curr_agent_states_n[0]
          mean_temp_n_m2 = mean_temp_hist_n[1]
          hour_n = curr_agent_states_n[1]
          oa_n = curr_agent_states_n[2]   
          sol_n= curr_agent_states_n[4]   
          dr_m1 = curr_agent_states_n[6]          
          dr_m0 = curr_agent_states_n[7]         
          soc_n = curr_agent_states_n[8]          
          
          act_1 = action[0]
          act_2 = action[1]

          r_state_n = np.array([[mean_temp_n,hour_n,oa_n,sol_n,dr_m1,dr_m0,soc_n,act_1,act_2]])
          t_state_n = np.array([[mean_temp_n_m2,mean_temp_n,hour_n,oa_n,sol_n,act_1]]) 

          return [t_state_n, r_state_n]

     def model_save_weights(self,name):
          self.model.save_weights(name)

     def model_load_weights(self,name):
          self.model.load_weights(name)

     def load_data(self,episodes,path):
          file_names = os.listdir(path+'04_Mem/')
          df = pd.DataFrame()
          for file_name in file_names[0:episodes]:
               print ("loading file for r model: {}".format(file_name))
               df1 = pd.read_pickle(path+'/04_Mem/'+str(file_name))
               df1 = self.pre_process(df1)
               df = pd.concat([df,df1])

          df = outlier_clearing(df)
          for i in range(len(df)):
               r_state = df.iloc[i]['r_state_v1']
               r_pred = df.iloc[i]['r_pred']               
               self.append_sample(r_state=r_state,r_pred=r_pred)
     

