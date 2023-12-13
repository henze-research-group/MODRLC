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
import numpy as np; import pandas as pd 
import matplotlib.pyplot as plt
from tensorflow.keras import optimizers
from collections import deque
import numpy as np;import pandas as pd
from collections import OrderedDict
import math; import random; from statistics import mean


class LSTM_Model():
     def __init__(self,state_size,pred_size,batch_size,buffer_size):
          self.state_size = state_size
          self.pred_size = pred_size
          self.learning_rate = 0.000001
          self.batch_size = batch_size
          self.memory = deque(maxlen=buffer_size)
          self.model =  self.build_model()

     def build_model(self):
          model = Sequential()
          model.add(LSTM(units=100,batch_input_shape=(None,self.state_size,1),return_sequences=True))    
          model.add(LSTM(units=100,return_sequences=False))             
          model.add(Dense(150, activation="tanh", kernel_initializer='he_uniform'))          
          model.add(Dense(100, activation="linear", kernel_initializer='he_uniform'))
          model.add(Dense(self.pred_size, activation="linear", kernel_initializer='he_uniform'))
          model.summary()
          model.compile(loss='mse',optimizer = tf.keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07))
          return model

     def append_sample(self,lstm_state,lstm_true_pred):
        self.memory.append((lstm_state,lstm_true_pred))

     def train_model(self,training_epochs):
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
          history = self.model.fit(np.array(states),np.array(preds),epochs=training_epochs,verbose=1)
          loss = history.history['loss'][0]
          return loss

     def predict(self,input_state):
          return self.model.predict(input_state)

     def model_save_weights(self,name):
        self.model.save_weights(name)

     def model_load_weights(self,name):
        self.model.load_weights(name)

     

