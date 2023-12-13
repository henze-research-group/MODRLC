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
verbose = 1

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
          model.add(LSTM(units=200,batch_input_shape=(None,self.state_size,1),return_sequences=True))    
          model.add(LSTM(units=200,return_sequences=False))             
          model.add(Dense(500, activation="relu", kernel_initializer='he_uniform'))   
          model.add(Dense(500, activation="relu", kernel_initializer='he_uniform'))  
          model.add(Dense(500, activation="relu", kernel_initializer='he_uniform'))                   
          model.add(Dense(450, activation="linear", kernel_initializer='he_uniform'))
          model.add(Dense(self.pred_size, activation="linear", kernel_initializer='he_uniform'))
          model.summary()

          # optim = tf.keras.optimizers.experimental.SGD(learning_rate=self.learning_rate, momentum=0.7)
          # model.compile(loss='mae',optimizer = optim)

          model.compile(loss='mse',optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate, beta_1=0.9, beta_2=0.99, epsilon=1e-07))
          return model

     def append_sample(self,t_state,t_pred):
        self.memory.append((t_state,t_pred))

     def train_model(self,training_epochs):
          print ("t model memory size check: {}".format(len(self.memory)))
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
          history = self.model.fit(np.array(states),np.array(preds),epochs=int(training_epochs/2),verbose=verbose)
          loss = history.history['loss'][-1]
          cnt = 0 
          print ("cnt: {},loss: {};".format(cnt,loss))
          while loss>0.01:
               cnt = cnt+1
               history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=verbose)
               loss = history.history['loss'][-1]
               print ("cnt: {},loss: {};".format(cnt,loss))
               # print ();print ()
               if cnt==1:
                    break
          return loss

     def predict(self,input_state):
          return self.model.predict(input_state,verbose=0)

     def model_save_weights(self,name):
          self.model.save_weights(name)

     def model_load_weights(self,name):
          self.model.load_weights(name)

     def load_data(self,episodes,path):
          file_names = os.listdir(path+'04_Mem/')
          df = pd.DataFrame()
          for file_name in file_names[0:]:
               print ("loading file for t model: {}".format(file_name))
               df1 = pd.read_pickle(path+'/04_Mem/'+str(file_name))
               df = pd.concat([df,df1])
          
          df = outlier_clearing(df)

          for i in range(len(df)):
               t_state = df.iloc[i]['t_state']
               t_pred = df.iloc[i]['t_pred']               
               self.append_sample(t_state=t_state,t_pred=t_pred)
          

class reward_model():
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
          model.add(Dense(1200,input_dim=self.state_size,activation="tanh", kernel_initializer='he_uniform'))              
          model.add(Dense(1800, activation="tanh", kernel_initializer='he_uniform'))   
          model.add(Dense(2000, activation="relu", kernel_initializer='he_uniform')) 
          model.add(Dense(2000, activation="relu", kernel_initializer='he_uniform')) 
          model.add(Dense(1800, activation="linear", kernel_initializer='he_uniform'))      
          model.add(Dense(1800, activation="linear", kernel_initializer='he_uniform'))
          model.add(Dense(self.pred_size, activation="linear", kernel_initializer='he_uniform')) 
          model.summary()

          
          loss = tf.keras.losses.Huber(delta=50.0)

          # model.compile(loss='mse',optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate, beta_1=0.9, beta_2=0.99, epsilon=1e-06))
          model.compile(loss=loss,optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate, beta_1=0.9, beta_2=0.99, epsilon=1e-06))
          
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
          history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=verbose)
          loss = history.history['loss'][-1]
          cnt = 0 
          counter = 0
          print ("cnt: {},loss: {};".format(cnt,loss))
          while loss>20:
               cnt=cnt+1
               history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=verbose)
               loss = history.history['loss'][-1]
               print ("cnt: {},loss: {};".format(cnt,loss))
               print ();print ()
               # if loss > 300: 
               #      counter+=1
               #      if counter == 10:
               #           break
               if cnt==1:
                    break
          return loss

     def predict(self,input_state):
          return self.model.predict(input_state,verbose=0)

     def model_save_weights(self,name):
          self.model.save_weights(name)

     def model_load_weights(self,name):
          self.model.load_weights(name)

     def load_data(self,episodes,path):
          file_names = os.listdir(path+'04_Mem/')   
          # print ("file names: {}; path: {}".format(file_names,path+'04_Mem'))  
          df = pd.DataFrame()   
          for file_name in file_names[0:]:
               print ("loading file for r model: {}".format(file_name))
               df1 = pd.read_pickle(path+'/04_Mem/'+str(file_name))
               df = pd.concat([df,df1])

          df = outlier_clearing(df)
          for i in range(len(df)):
               r_state = df.iloc[i]['r_state']
               r_pred = df.iloc[i]['r_pred']               
               self.append_sample(r_state=r_state,r_pred=r_pred)


