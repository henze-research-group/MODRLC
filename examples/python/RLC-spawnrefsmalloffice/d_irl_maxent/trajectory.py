"""
Trajectories representing expert demonstrations and automated generation
thereof.
"""

import numpy as np
from itertools import chain
import os ;from os import listdir
import pandas as pd 
tab_id = pd.read_csv('RL_Data/00_Tables/tab_id.csv')


class Trajectory:
    """
    A trajectory consisting of states, corresponding actions, and outcomes.

    Args:
        transitions: The transitions of this trajectory as an array of
            tuples `(state_from, action, state_to)`. Note that `state_to` of
            an entry should always be equal to `state_from` of the next
            entry.
    """
    def __init__(self, transitions):
        self._t = transitions

    def transitions(self):
        """
        The transitions of this trajectory.

        Returns:
            All transitions in this trajectory as array of tuples
            `(state_from, action, state_to)`.
        """
        return self._t

    def states(self):
        """
        The states visited in this trajectory.

        Returns:
            All states visited in this trajectory as iterator in the order
            they are visited. If a state is being visited multiple times,
            the iterator will return the state multiple times according to
            when it is visited.
        """
        return map(lambda x: x[0], chain(self._t, [(self._t[-1][2], 0, 0)]))

    def __repr__(self):
        return "Trajectory({})".format(repr(self._t))

    def __str__(self):
        return "{}".format(self._t)

        

def generate_trajectory(tot_data,last_count):
    trajectory = []
    # last_count = 0
    for i in range(last_count+1,len(tot_data)):
        curr_state = int(tot_data.iloc[i]['index_curr_s'])
        next_state = int(tot_data.iloc[i]['index_next_s'])
        act = tot_data.iloc[i]['act']
        done = tot_data.iloc[i]['done']
        trajectory += [(curr_state, act, next_state)]    
        if done==True:
            last_count = i 
            # print ("last count: {}".format(last_count))
            break 

    return Trajectory(trajectory)


def generate_trajectories():
    path = 'RL_Data/01_RBC/03_Data/'   

    # print (listdir(os.getcwd())+'')
    files=listdir(os.getcwd()+'/'+path)
    tot_data = pd.DataFrame()

    for file_name in range(len(files)):
        data = pd.read_csv(path+files[file_name],converters={'action': eval})          
        data['index_curr_s'] = data.apply(lambda x : get_index([x['s0'],x['s1'],x['s2'],x['s3']]),axis = 1)
        data['index_next_s'] = data.index_curr_s.shift(-1)
        data = data[1:-1]  
        tot_data = pd.concat([data,tot_data])
        tot_data.reset_index(drop=True,inplace=True)

    tot_data['act'] = tot_data.apply(lambda x: x['action'][0],axis=1)
    tot_data['done'] = np.where(tot_data['senHouDec_y']>23.8, True, False)

    tjs = []
    end_episodes = list(tot_data[tot_data['done']==True].index)[:-1]
    end_episodes.insert(0,0)
    # print (end_episodes)
    for last_count in end_episodes:
        tjs.append(generate_trajectory(tot_data,last_count))

    return tjs

def get_index(s):    
    instance = pd.Series({'s0': s[0], 's1':s[1], 's2': s[2],'s3':s[3]})
    id1 = tab_id.loc[(tab_id==instance).all(axis=1)]

    # find the row
    id = tab_id.loc[(tab_id==instance).all(axis=1)].index[0]
    return id 


def policy_adapter(policy):
    """
    A policy adapter for deterministic policies.

    Adapts a deterministic policy given as array or map
    `policy[state] -> action` for the trajectory-generation functions.

    Args:
        policy: The policy as map/array
            `policy[state: Integer] -> action: Integer`
            representing the policy function p(state).

    Returns:
        A function `(state: Integer) -> action: Integer` acting out the
        given policy.
    """
    return lambda state: policy[state]


def stochastic_policy_adapter(policy):
    """
    A policy adapter for stochastic policies.

    Adapts a stochastic policy given as array or map
    `policy[state, action] -> probability` for the trajectory-generation
    functions.

    Args:
        policy: The stochastic policy as map/array
            `policy[state: Integer, action: Integer] -> probability`
            representing the probability distribution p(action | state) of
            an action given a state.

    Returns:
        A function `(state: Integer) -> action: Integer` acting out the
        given policy, choosing an action randomly based on the distribution
        defined by the given policy.
    """
    return lambda state: np.random.choice([*range(policy.shape[1])], p=policy[state, :])
