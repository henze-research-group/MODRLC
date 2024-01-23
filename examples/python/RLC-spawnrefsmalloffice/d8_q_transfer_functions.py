import pandas as pd
import numpy as np 
import math; import random
from d6_functions import *
import tensorflow
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential

state_size_dqn = 5
action_size_dqn = 2
path = 'RL_Data/00_Tables/'

def model_DQN():
  model_dqn = Sequential()
  model_dqn.add(Dense(300,input_dim=state_size_dqn,activation="tanh",kernel_initializer = 'he_uniform'))
  model_dqn.add(Dense(350, activation="tanh", kernel_initializer='he_uniform'))
  model_dqn.add(Dense(400, activation="tanh", kernel_initializer='he_uniform'))
  model_dqn.add(Dense(500, activation="tanh", kernel_initializer='he_uniform'))
  model_dqn.add(Dense(450, activation="linear", kernel_initializer='he_uniform'))
  model_dqn.add(Dense(400, activation="linear", kernel_initializer='he_uniform'))
  model_dqn.add(Dense(action_size_dqn, activation="linear", kernel_initializer='he_uniform'))
  model_dqn.summary()
  model_dqn.load_weights(path+'model_dqn.h5')
  return model_dqn

def gen_train_samples(iter1,rpt):
  states_l = []
  preds_l = []

  reward = np.load(path+'final_reward_maxent.npy')
  table = np.load(path+'table.npy')
  value_iteration(p=table, reward=reward, discount=0.9, eps=1e-3)

  iter_no_2 = len(table)
  for iter in range(iter1):    
    print (iter)
    gen_state_n,index_states = form_one_state()    
    s0 = get_index_2(index_states) 
    q_value = get_q_value(state=s0)

    states_l.append(gen_state_n)
    preds_l.append(q_value)

  for x in range(rpt):
    for s0 in range(iter_no_2):    
      index_state = index_to_state(s0)  
      gen_state = form_gen_state(index_state)     
      q_value = get_q_value(state=s0)
      gen_state_n = norm(gen_state)
      states_l.append(gen_state_n)
      preds_l.append(q_value)

  np.save(path+'states_l.npy',states_l)
  np.save(path+'preds_l.npy',preds_l)

  return states_l,preds_l

def norm(gen_state):
  dr_normal =18
  min_temp, max_temp = 16,33
  min_oa, max_oa = 15,35
  low =  np.array([min_temp,0, min_oa, 0, 0])
  high = np.array([max_temp,24,max_oa, dr_normal,1])
  return (gen_state - low)/(high-low)

def get_q_value(state):
  q = np.load(path+'q_value.npy')
  return np.array([q[0][0][state],q[1][0][state]])

def get_index_2(s):
  instance = pd.Series({'s0': s[0][0], 's1':s[0][1], 's2': s[0][2],'s3':s[0][3]})
  # find the row
  id = tab_id.loc[(tab_id==instance).all(axis=1)].index[0]
  return id 

def value_iteration(p, reward, discount, eps=1e-3):
  n_states, _, n_actions = p.shape
  v = np.zeros(n_states)
  
  p = [np.matrix(p[:, :, a]) for a in range(n_actions)]
  iter = 0 
  delta = np.inf
  while delta > eps:      # iterate until convergence
      v_old = v
      iter +=1

      # compute state-action values (note: we actually have Q[a, s] here)
      q = discount * np.array([p[a] @ v for a in range(n_actions)])

      # compute state values
      v = reward + np.max(q, axis=0)[0]

      # compute maximum delta
      delta = np.max(np.abs(v_old - v))

  np.save(path+'q_value.npy',q)
  np.save(path+'v_value.npy',v)

  return v,q


def form_gen_state(index_state):                
  ls = []
  for index_s in range(len(index_state)):
    st = index_state[index_s]
    if index_s==0:
      stc = state1_temp(st)
      ls.append(stc)       
    elif index_s==1:
      stc = state2_hour(st)
      ls.append(stc)
    elif index_s==2:
      stc = state3_oa(st)
      ls.append(stc)
    else:
      stc = state4_dr(st)
      for stc_ in stc:
        ls.append(stc_)

  if ls[3]==0:      
    dr_rand_start = np.random.uniform(16.5,17.5)
    dr_rand_end = dr_rand_start + np.random.uniform(2,3)
    ls[1] = np.random.uniform(dr_rand_start,dr_rand_end)
  return np.array(ls)


def form_one_state():
  ''' Variable declaration '''
  dr_normal = 18 
  min_oa, max_oa = 10,35
  min_temp, max_temp = 273.15+15, 273.15+36
  low =  np.array([min_temp,0, min_oa, 0, 0])
  high = np.array([max_temp,24,max_oa, dr_normal,1])
  ''' Variable declaration '''

  ''' Variable Generation '''
  dr_rand_start = np.random.uniform(16.5,17.5)
  dr_rand_end = dr_rand_start + np.random.uniform(2,3)

  mean_temp  = np.random.uniform(min_temp,max_temp)
  hour_dec  = np.random.uniform(0,24)
  oa =  np.random.uniform(min_oa,max_oa)


  if (hour_dec >= dr_rand_start) and (hour_dec < dr_rand_end):
      dr_0 = 1
  else:
      dr_0 = 0

  dr_1 =  dr_rand_start - hour_dec
  if (dr_1 <0):
      dr_1 = 0
  ''' Variable Generation '''


  ''' Form general state and index states '''
  T_index = get_temp_index(temp=mean_temp-273.15)
  hr_index = get_occ_signal(time=hour_dec)
  oa_index = get_oa_index(oa=oa)   
  dr_index = get_dr_index_2(dr_m1=dr_0,dr_0=dr_1,hour_dec=hour_dec)

  gen_state = np.array([mean_temp,hour_dec,oa,dr_1,dr_0])
  gen_state_n = (gen_state-low)/(high-low)
  index_states = np.array([[T_index,hr_index,oa_index,dr_index]])
  ''' Form general state and index states ''' 
  
  return gen_state_n,index_states



def state1_temp(st):
  if st==0:
    st_c = np.random.uniform(14,20)
  elif st==1:
    st_c = np.random.uniform(20,21.5)
  elif st==2:
    st_c = np.random.uniform(21.5,23)
  elif st==3:
    st_c = np.random.uniform(23,24.5)
  elif st==4:
    st_c = np.random.uniform(24.5,26)
  elif st==5:
    st_c = np.random.uniform(26,32)
  return st_c

def state2_hour(st):
  if st==0:
    st_c = np.random.choice([np.random.uniform(0,6),np.random.uniform(22,24)])
  elif st==1:
    st_c = np.random.uniform(6,22)  
  return st_c


def state3_oa(st):
  if st==0:
    st_c = np.random.uniform(10,21)
  elif st==1:
    st_c =np.random.uniform(21,24)  
  else:
    st_c =np.random.uniform(24,35)
  return st_c


def state4_dr(st):
  dr_rand_start = np.random.uniform(16.5,17.5)
  dr_rand_end = dr_rand_start + np.random.uniform(2,3)
  if st==0:
    dr_0 = 1
    dr_1 = 0 
  elif st==1:
    dr_1 = np.random.uniform(dr_rand_start-1,dr_rand_start)  
    dr_0 = 0
  elif st==2:
    dr_1 = np.random.uniform(dr_rand_start-3,dr_rand_start-1) 
    dr_0 = 0
  elif st==3:
    dr_1 = np.random.choice([np.random.uniform(0,dr_rand_start-3),np.random.uniform(dr_rand_end,24-300/3600)])
    if dr_1 > dr_rand_end:
      dr_1 = 0
    dr_0 = 0
  elif st==4:
    dr_1 = 0
    dr_0 = 0
  return dr_1,dr_0


