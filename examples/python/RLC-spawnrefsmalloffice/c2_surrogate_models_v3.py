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


def get_r_model(lr,state_size,pred_size):          
     model = Sequential()
     model.add(Dense(800,input_dim=state_size,activation="tanh",kernel_initializer = 'he_uniform'))                            
     model.add(Dense(1200, activation="relu", kernel_initializer='he_uniform'))          
     model.add(Dense(1200, activation="relu", kernel_initializer='he_uniform'))
     model.add(Dense(800, activation="linear", kernel_initializer='he_uniform'))
     model.add(Dense(pred_size, activation="linear", kernel_initializer='he_uniform'))
     model.summary()
     loss = tf.keras.losses.Huber(delta=50)

     model.compile(loss=loss,optimizer = tf.keras.optimizers.Adam(learning_rate=lr, beta_1=0.9, beta_2=0.999, epsilon=1e-07))

     return model          