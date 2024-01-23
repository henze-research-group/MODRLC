#!/usr/bin/env python

from d_irl_maxent import gridworld as W
from d_irl_maxent import maxent as M
from d_irl_maxent import plot as P
from d_irl_maxent import trajectory as T
from d_irl_maxent import solver as S
from d_irl_maxent import optimizer as O

import numpy as np
import matplotlib.pyplot as plt


def setup_mdp():   
    # create our world
    world = W.buiding_env()

    # set up the reward function
    reward = np.zeros(world.n_states)

    state_0 = 6 # mean temp
    state_1 = 2 # time 
    state_2 = 3 # oa
    state_3 = 4  # DR signal 01
    

    size =  state_0*state_1*state_2*state_3
    
    # set up terminal states
    terminal = [size-1]

    return world, reward, terminal


def generate_trajectories():           
    tjs = T.generate_trajectories()
    return tjs


def maxent(world, terminal, trajectories):
    """
    Maximum Entropy Inverse Reinforcement Learning
    """
    # set up features: we use one feature vector per state
    features = W.state_features(world)

    # print ("terminal {}".format(len(terminal)))
    # print ("trajectories {}".format(trajectories))
    # print ("features shape {}".format(features.shape))

    # choose our parameter initialization strategy:
    #   initialize parameters with constant
    init = O.Constant(1.0)

    # choose our optimization strategy:
    #   we select exponentiated gradient descent with linear learning-rate decay
    optim = O.ExpSga(lr=O.linear_decay(lr0=0.008))

    # actually do some inverse reinforcement learning
    reward = M.irl(world.p_transition, features, terminal, trajectories, optim, init)

    np.save("final_reward_maxent.npy",reward)

    return reward


def maxent_causal(world, terminal, trajectories, discount=0.9):
    """
    Maximum Causal Entropy Inverse Reinforcement Learning
    """
    # set up features: we use one feature vector per state
    features = W.state_features(world)

    # choose our parameter initialization strategy:
    #   initialize parameters with constant
    init = O.Constant(0.1)

    # choose our optimization strategy:
    #   we select exponentiated gradient descent with linear learning-rate decay
    optim = O.ExpSga(lr=O._decay(lr0=0.0001))

    # print ("features: {}".format(features))

    # actually do some inverse reinforcement learning
    reward = M.irl_causal(world.p_transition, features, terminal, trajectories, optim, init, discount)

    return reward


def main():
    # common style arguments for plotting
    style = {
        'border': {'color': 'red', 'linewidth': 0.5},
    }

    # set-up mdp
    world, reward, terminal = setup_mdp()

    print ("reward main: {}".format(reward))

    # print ("world: {}".format(world))   
    

    # generate "expert" trajectories
    trajectories = generate_trajectories()

    # print ("Trajectories: {}".format(trajectories))  

    # maximum entropy reinforcement learning (non-causal)
    reward_maxent = maxent(world, terminal, trajectories)
    

    # show the computed reward
    # ax = plt.figure(num='MaxEnt Reward').add_subplot(111)
    # P.plot_state_values(ax, world, reward_maxent, **style)
    # plt.draw()

    # print ("Check 02")
    # print ("Terminal: {}".format(terminal))

    # maximum casal entropy reinforcement learning (non-causal)
    # reward_maxcausal = maxent_causal(world, terminal, trajectories)

    print ("reward maxent: {}".format (reward_maxent))

    print ("Check 03")

    # show the computed reward
    # ax = plt.figure(num='MaxEnt Reward (Causal)').add_subplot(111)
    # P.plot_state_values(ax, world, reward_maxcausal, **style)
    # plt.draw()

    # plt.show()


if __name__ == '__main__':
    main()
