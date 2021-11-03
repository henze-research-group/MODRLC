# -*- coding: utf-8 -*-
"""
This module is an example python-based testing interface.  It uses the
``requests`` package to make REST API calls to the test case container,
which mus already be running.  A controller is tested, which is 
imported from a different module.
  
"""

# GENERAL PACKAGE IMPORT
# ----------------------
import requests; import os
import time ; import random
import json,collections
from collections import deque
import os.path as path
import sys
import pandas as pd; import numpy as np
import collections; from collections import deque
import gym; from gym import spaces
import keras
from keras.layers import Dense
from keras.optimizers import Adam
from keras.models import Sequential



BOPTEST_path = path.abspath(path.join(os.getcwd(), "../.."))
sys.path.append(BOPTEST_path+"/examples/python")


class DQN_Agent:
    def __init__(self,state_size,action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = 0.00001
        self.memory = deque(maxlen=4000)
        self.target_model = self.build_model()
        self.epsilon = 0.99 # initial epsilon
        self.epsilon_decay = 0.95
        self.train_start =288*3 #800
        self.batch_size = 400  #2000
        self.discount_factor = 0.9995
        self.epsilon_min = 0.001  # keep epsilon exploration to 0.1 % at the end
        self.model = self.build_model()



    def build_model(self):
        model = Sequential()
        model.add(Dense(300,input_dim=self.state_size,activation="relu",kernel_initializer = 'he_uniform'))
        model.add(Dense(350, activation="tanh", kernel_initializer='he_uniform'))
        model.add(Dense(450, activation="tanh", kernel_initializer='he_uniform'))
        model.add(Dense(600, activation="tanh", kernel_initializer='he_uniform'))
        model.add(Dense(500, activation="tanh", kernel_initializer='he_uniform'))
        model.add(Dense(400, activation="linear", kernel_initializer='he_uniform'))
        model.add(Dense(300, activation="linear", kernel_initializer='he_uniform'))
        model.add(Dense(self.action_size, activation="linear", kernel_initializer='he_uniform'))
        model.summary()
        model.compile(loss='mse',optimizer = Adam(lr=self.learning_rate))
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def get_memory(self):
        return self.memory


    def get_action(self,state):
        if np.random.rand() <= self.epsilon:
            print ("Random Action")
            return random.randrange(self.action_size)
        else:
            print("Selective Action")
            q_value = self.model.predict(state)
        return np.argmax(q_value[0])

    def append_sample(self,state,action,reward,next_state,done):
        self.memory.append((state,action,reward,next_state,done))

    def exploration_value(self):
        z = self.epsilon
        return z


    def train_model(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon = self.epsilon * self.epsilon_decay

        if len(self.memory) < self.train_start:
            return
        batch_size = min(self.batch_size,len(self.memory))
        mini_batch = random.sample(self.memory,batch_size)

        states,targets_f = [],[]
        for state,action,reward,next_state,done in mini_batch:
            target = reward
            if not done:
                target = (reward + self.discount_factor*np.amax(self.target_model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][int(action)] = target

            #print("Train Action")
            #print(action)
            #print("Target_f")
            #print(target_f)

            states.append(state[0])
            targets_f.append(target_f[0])

        history = self.model.fit(np.array(states),np.array(targets_f),epochs =50,verbose=1)

        loss = history.history['loss'][0]

        return loss

    def target_predict_qvalue(self,state):
        q_value = self.model.predict(state)
        return q_value


    def model_save_weights(self,name):
        self.model.save_weights(name)

    def model_load_weights(self,name):
        self.model.load_weights(name)









