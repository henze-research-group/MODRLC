import pandas as pd
import numpy as np 
import math; import random
from d8_q_transfer_functions import *
from tensorflow.keras.optimizers import Adam

path = 'RL_Data/00_Tables/'
model_dqn = model_DQN()

second_pass = True

if second_pass==True:
  states_l = np.load(path+'states_l.npy')
  preds_l = np.load(path+'preds_l.npy')
else:
  states_l, preds_l = gen_train_samples(iter1=5000,rpt=50)


learning_rate = 0.000015
model_dqn.compile(loss='mse',optimizer = Adam(learning_rate=learning_rate))  
model_dqn.load_weights('model_dqn.h5')
model_dqn.fit(states_l,preds_l,epochs =250,verbose=1,batch_size=150)
model_dqn.save_weights('model_dqn.h5')