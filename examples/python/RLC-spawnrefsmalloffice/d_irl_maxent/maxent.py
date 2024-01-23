"""
Maximum Entropy Inverse Reinforcement Learning and Maximum Causal Entropy
Inverse Reinforcement Learning.

Based on the corresponding paper by B. Ziebart et al. (2008) and the Thesis
by Ziebart (2010).
"""

import numpy as np
from itertools import product
import pandas as pd 

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.absolute()/'d_irl_maxent'))

print (sys.path)

state_0 = 6 # mean temp
state_1 = 2 # time 
state_2 = 3 # oa
state_3 = 5  # DR signal 01
no_of_states= state_0*state_1*state_2*state_3

cnt = 0 
tab_id = pd.DataFrame(columns=['s0', 's1','s2','s3'],index=range(no_of_states))
for s0 in range (state_0):
  for s1 in range(state_1):   
    for s2 in range(state_2):
      for s3 in range(state_3):        
        tab_id.iloc[cnt]['s1']= s1
        tab_id.iloc[cnt]['s0']= s0
        tab_id.iloc[cnt]['s2']= s2 
        tab_id.iloc[cnt]['s3']= s3
        # tab_id.iloc[cnt]['s4']= s4
        cnt +=1


def index_to_state(index):
  st_0 = tab_id.iloc[index].s0
  st_1 = tab_id.iloc[index].s1
  st_2 = tab_id.iloc[index].s2
  st_3 = tab_id.iloc[index].s3
  # st_4 = tab_id.iloc[index].s4  

  return np.array([st_0,st_1,st_2,st_3])

terminal_states = []
for state_index in range(no_of_states):
  state = index_to_state(state_index)
  if state[3]==4:
    terminal_states.append(state_index)



# -- common functions ----------------------------------------------------------

def feature_expectation_from_trajectories(features, trajectories):
    """
    Compute the feature expectation of the given trajectories.

    Simply counts the number of visitations to each feature-instance and
    divides them by the number of trajectories.

    Args:
        features: The feature-matrix (e.g. as numpy array), mapping states
            to features, i.e. a matrix of shape (n_states x n_features).
        trajectories: A list or iterator of `Trajectory` instances.

    Returns:
        The feature-expectation of the provided trajectories as map
        `[state: Integer] -> feature_expectation: Float`.
    """
    n_states, n_features = features.shape

    fe = np.zeros(n_features)

    for t in trajectories:
        for s in t.states():
            fe += features[s, :]

    return fe / len(trajectories)


def initial_probabilities_from_trajectories(n_states, trajectories):
    """
    Compute the probability of a state being a starting state using the
    given trajectories.

    Args:
        n_states: The number of states.
        trajectories: A list or iterator of `Trajectory` instances.

    Returns:
        The probability of a state being a starting-state as map
        `[state: Integer] -> probability: Float`.
    """
    p = np.zeros(n_states)

    for t in trajectories:
        p[t.transitions()[0][0]] += 1.0

    return p / len(trajectories)


def expected_svf_from_policy(p_transition, p_initial, terminal, p_action, eps=1e-5):
    """
    Compute the expected state visitation frequency using the given local
    action probabilities.

    This is the forward pass of Algorithm 1 of the Maximum Entropy IRL paper
    by Ziebart et al. (2008). Alternatively, it can also be found as
    Algorithm 9.3 in in Ziebart's thesis (2010).

    It has been slightly adapted for convergence, by forcing transition
    probabilities from terminal stats to be zero.

    Args:
        p_transition: The transition probabilities of the MDP as table
            `[from: Integer, to: Integer, action: Integer] -> probability: Float`
            specifying the probability of a transition from state `from` to
            state `to` via action `action` to succeed.
        p_initial: The probability of a state being an initial state as map
            `[state: Integer] -> probability: Float`.
        terminal: A list of terminal states.
        p_action: Local action probabilities as map
            `[state: Integer, action: Integer] -> probability: Float`
            as returned by `local_action_probabilities`.
        eps: The threshold to be used as convergence criterion. Convergence
            is assumed if the expected state visitation frequency changes
            less than the threshold on all states in a single iteration.

    Returns:
        The expected state visitation frequencies as map
        `[state: Integer] -> svf: Float`.
    """
    n_states, _, n_actions = p_transition.shape

    # 'fix' our transition probabilities to allow for convergence
    # we will _never_ leave any terminal state
    p_transition = np.copy(p_transition)
    p_transition[terminal, :, :] = 0.0

    # set-up transition matrices for each action
    p_transition = [np.array(p_transition[:, :, a]) for a in range(n_actions)]

    # print ("p_transition check: {}".format(p_transition))
    # print ("p_transition shape check: {}".format(p_transition.shape))
    print ()

    # actual forward-computation of state expectations
    d = np.zeros(n_states)

    delta = np.inf
    while delta > eps:
        d_ = [p_transition[a].T.dot(p_action[:, a] * d) for a in range(n_actions)]
        # print ("d_:{}".format(d_))
        d_ = p_initial + np.array(d_).sum(axis=0)

        delta, d = np.max(np.abs(d_ - d)), d_

    return d


# -- plain maximum entropy (Ziebart et al. 2008) -------------------------------

def local_action_probabilities(p_transition, terminal, reward):
    """
    Compute the local action probabilities (policy) required for the edge
    frequency calculation for maximum entropy reinfocement learning.

    This is the backward pass of Algorithm 1 of the Maximum Entropy IRL
    paper by Ziebart et al. (2008).

    Args:
        p_transition: The transition probabilities of the MDP as table
            `[from: Integer, to: Integer, action: Integer] -> probability: Float`
            specifying the probability of a transition from state `from` to
            state `to` via action `action` to succeed.
        terminal: A set/list of terminal states.
        reward: The reward signal per state as table
            `[state: Integer] -> reward: Float`.

    Returns:
        The local action probabilities (policy) as map
        `[state: Integer, action: Integer] -> probability: Float`
    """
    n_states, _, n_actions = p_transition.shape

    # print ("p transition shape")
    # print (p_transition.shape)


    # print ("reward in local causal prob ")
    # print (reward.shape)
    # print (reward)

    er = np.exp(reward)
    p = [np.array(p_transition[:, :, a]) for a in range(n_actions)]   

    # print ("p shape:{}".format(p[0].shape)) 
    print ()
    # print ("p:{}".format(p)) 
    

    # initialize at terminal states
    zs = np.zeros(n_states)
    

    for terminal in terminal_states:
        zs[terminal] = 1.0

    # print ("zs: {}".format(zs))

    # perform backward pass
    # This does not converge, instead we iterate a fixed number of steps. The
    # number of steps is chosen to reflect the maximum steps required to
    # guarantee propagation from any state to any other state and back in an
    # arbitrary MDP defined by p_transition.
    for ct in range(100):        
        za = np.array([er * p[a].dot(zs) for a in range(n_actions)],dtype=np.float128).T
        # print ("za: {}".format(za))
        za = np.where(za==0, 0.0000001, za)       

        power = float(int(np.log10(za.max())))
        if power>50:
            # print ("power correction")
            za = za/(10**power)

        zs = za.sum(axis=1)

        # print ("max power: {}".format(power))
        # print (ct)
        # print ()

    print ("1 stage completed")
    

    # print ("za: {}".format(za))
    # print ()

    # print ("zs: {}".format(zs))
    # print ("er: {}".format(er))

    # compute local action probabilities
    return za / zs[:, None]


def compute_expected_svf(p_transition, p_initial, terminal, reward, eps=1e-4):
    """
    Compute the expected state visitation frequency for maximum entropy IRL.

    This is an implementation of Algorithm 1 of the Maximum Entropy IRL
    paper by Ziebart et al. (2008).

    This function combines the backward pass implemented in
    `local_action_probabilities` with the forward pass implemented in
    `expected_svf_from_policy`.

    Args:
        p_transition: The transition probabilities of the MDP as table
            `[from: Integer, to: Integer, action: Integer] -> probability: Float`
            specifying the probability of a transition from state `from` to
            state `to` via action `action` to succeed.
        p_initial: The probability of a state being an initial state as map
            `[state: Integer] -> probability: Float`.
        terminal: A list of terminal states.
        reward: The reward signal per state as table
            `[state: Integer] -> reward: Float`.
        eps: The threshold to be used as convergence criterion for the
            expected state-visitation frequency. Convergence is assumed if
            the expected state visitation frequency changes less than the
            threshold on all states in a single iteration.

    Returns:
        The expected state visitation frequencies as map
        `[state: Integer] -> svf: Float`.
    """
    p_action = local_action_probabilities(p_transition, terminal, reward)

    # print ("p_action {}".format(p_action))
    return expected_svf_from_policy(p_transition, p_initial, terminal, p_action, eps)


def irl(p_transition, features, terminal, trajectories, optim, init, eps=0.01, eps_esvf=1e-5):
    """
    Compute the reward signal given the demonstration trajectories using the
    maximum entropy inverse reinforcement learning algorithm proposed in the
    corresponding paper by Ziebart et al. (2008).

    Args:
        p_transition: The transition probabilities of the MDP as table
            `[from: Integer, to: Integer, action: Integer] -> probability: Float`
            specifying the probability of a transition from state `from` to
            state `to` via action `action` to succeed.
        features: The feature-matrix (e.g. as numpy array), mapping states
            to features, i.e. a matrix of shape (n_states x n_features).
        terminal: A list of terminal states.
        trajectories: A list of `Trajectory` instances representing the
            expert demonstrations.
        optim: The `Optimizer` instance to use for gradient-based
            optimization.
        init: The `Initializer` to use for initialization of the reward
            function parameters.
        eps: The threshold to be used as convergence criterion for the
            reward parameters. Convergence is assumed if all changes in the
            scalar parameters are less than the threshold in a single
            iteration.
        eps_svf: The threshold to be used as convergence criterion for the
            expected state-visitation frequency. Convergence is assumed if
            the expected state visitation frequency changes less than the
            threshold on all states in a single iteration.

    Returns:
        The reward per state as table `[state: Integer] -> reward: Float`.
    """
    n_states, _, n_actions = p_transition.shape
    _, n_features = features.shape

    # compute static properties from trajectories
    e_features = feature_expectation_from_trajectories(features, trajectories)
    p_initial = initial_probabilities_from_trajectories(n_states, trajectories)


    # basic gradient descent
    theta = init(n_features)

    

    # print ("e features: {}".format(e_features))
    # print ("p initial: {}".format(p_initial))

    # print ("theta: {}".format(theta))

    # print ("features: {}".format(features))
    # print ("features x theta: {}".format(features.dot(theta)))



    delta = np.inf
    ct2 = 0 
    optim.reset(theta)
    while delta > eps:
        ct2 +=1
        theta_old = theta.copy()

        print ("count in main: {}".format(ct2))

        # compute per-state reward
        reward = features.dot(theta)
        print ("reward in iteration: {}".format(reward))
        print ("saving rewards")
        np.save("reward_maxent.npy",reward)

        # compute the gradient
        e_svf = compute_expected_svf(p_transition, p_initial, terminal, reward, eps_esvf)

        # print ("e_svf: {}".format(e_svf))'

        print ("delta: {}".format(delta))

        grad = e_features - features.T.dot(e_svf)

        # perform optimization step and compute delta for convergence
        optim.step(grad)
        delta = np.max(np.abs(theta_old - theta))


    # re-compute per-state reward and return
    return features.dot(theta)


# -- maximum causal entropy (Ziebart 2010) -------------------------------------

def softmax(x1, x2):
    """
    Computes a soft maximum of both arguments.

    In case `x1` and `x2` are arrays, computes the element-wise softmax.

    Args:
        x1: Scalar or ndarray.
        x2: Scalar or ndarray.

    Returns:
        The soft maximum of the given arguments, either scalar or ndarray,
        depending on the input.
    """
    x_max = np.maximum(x1, x2)
    x_min = np.minimum(x1, x2)
    return x_max + np.log(1.0 + np.exp(x_min - x_max))


def local_causal_action_probabilities(p_transition, terminal, reward, discount, eps=1e-5):
    """
    Compute the local action probabilities (policy) required for the edge
    frequency calculation for maximum causal entropy reinfocement learning.

    This is Algorithm 9.1 from Ziebart's thesis (2010) combined with
    discounting for convergence reasons as proposed in the same thesis.

    Args:
        p_transition: The transition probabilities of the MDP as table
            `[from: Integer, to: Integer, action: Integer] -> probability: Float`
            specifying the probability of a transition from state `from` to
            state `to` via action `action` to succeed.
        terminal: Either the terminal reward function or a collection of
            terminal states. Iff `len(terminal)` is equal to the number of
            states, it is assumed to contain the terminal reward function
            (phi) as specified in Ziebart's thesis. Otherwise `terminal` is
            assumed to be a collection of terminal states from which the
            terminal reward function will be derived.
        reward: The reward signal per state as table
            `[state: Integer] -> reward: Float`.
        discount: A discounting factor as Float.
        eps: The threshold to be used as convergence criterion for the state
            partition function. Convergence is assumed if the state
            partition function changes less than the threshold on all states
            in a single iteration.

    Returns:
        The local action probabilities (policy) as map
        `[state: Integer, action: Integer] -> probability: Float`
    """
    n_states, _, n_actions = p_transition.shape

    # set up terminal reward function    
    if len(terminal) == n_states:
        reward_terminal = np.array(terminal, dtype=np.float)
    else:
        reward_terminal = -np.inf * np.ones(n_states)
        reward_terminal[terminal] = 0.0

    # set up transition probability matrices
    p = [np.array(p_transition[:, :, a]) for a in range(n_actions)]

    # compute state log partition V and state-action log partition Q
    v = -1e200 * np.ones(n_states)  # np.dot doesn't behave with -np.inf

    delta = np.inf
    while delta > eps:
        v_old = v

        q = np.array([reward + discount * p[a].dot(v_old) for a in range(n_actions)]).T

        v = reward_terminal
        for a in range(n_actions):
            v = softmax(v, q[:, a])

        # for some reason numpy chooses an array of objects after reduction, force floats here
        v = np.array(v, dtype=np.float)

        delta = np.max(np.abs(v - v_old))

    # compute and return policy
    return np.exp(q - v[:, None])


def compute_expected_causal_svf(p_transition, p_initial, terminal, reward, discount,
                                eps_lap=1e-5, eps_svf=1e-5):
    """
    Compute the expected state visitation frequency for maximum causal
    entropy IRL.

    This is a combination of Algorithm 9.1 and 9.3 of Ziebart's thesis
    (2010). See `local_causal_action_probabilities` and
    `expected_svf_from_policy` for more details.

    Args:
        p_transition: The transition probabilities of the MDP as table
            `[from: Integer, to: Integer, action: Integer] -> probability: Float`
            specifying the probability of a transition from state `from` to
            state `to` via action `action` to succeed.
        p_initial: The probability of a state being an initial state as map
            `[state: Integer] -> probability: Float`.
        terminal: Either the terminal reward function or a collection of
            terminal states. Iff `len(terminal)` is equal to the number of
            states, it is assumed to contain the terminal reward function
            (phi) as specified in Ziebart's thesis. Otherwise `terminal` is
            assumed to be a collection of terminal states from which the
            terminal reward function will be derived.
        reward: The reward signal per state as table
            `[state: Integer] -> reward: Float`.
        discount: A discounting factor as Float.
        eps_lap: The threshold to be used as convergence criterion for the
            state partition function. Convergence is assumed if the state
            partition function changes less than the threshold on all states
            in a single iteration.
        eps_svf: The threshold to be used as convergence criterion for the
            expected state-visitation frequency. Convergence is assumed if
            the expected state visitation frequency changes less than the
            threshold on all states in a single iteration.
    """
    p_action = local_causal_action_probabilities(p_transition, terminal, reward, discount, eps_lap)
    return expected_svf_from_policy(p_transition, p_initial, terminal, p_action, eps_svf)


def irl_causal(p_transition, features, terminal, trajectories, optim, init, discount,
               eps=1e-4, eps_svf=1e-5, eps_lap=1e-5):
    """
    Compute the reward signal given the demonstration trajectories using the
    maximum causal entropy inverse reinforcement learning algorithm proposed
    Ziebart's thesis (2010).

    Args:
        p_transition: The transition probabilities of the MDP as table
            `[from: Integer, to: Integer, action: Integer] -> probability: Float`
            specifying the probability of a transition from state `from` to
            state `to` via action `action` to succeed.
        features: The feature-matrix (e.g. as numpy array), mapping states
            to features, i.e. a matrix of shape (n_states x n_features).
        terminal: Either the terminal reward function or a collection of
            terminal states. Iff `len(terminal)` is equal to the number of
            states, it is assumed to contain the terminal reward function
            (phi) as specified in Ziebart's thesis. Otherwise `terminal` is
            assumed to be a collection of terminal states from which the
            terminal reward function will be derived.
        trajectories: A list of `Trajectory` instances representing the
            expert demonstrations.
        optim: The `Optimizer` instance to use for gradient-based
            optimization.
        init: The `Initializer` to use for initialization of the reward
            function parameters.
        discount: A discounting factor for the log partition functions as
            Float.
        eps: The threshold to be used as convergence criterion for the
            reward parameters. Convergence is assumed if all changes in the
            scalar parameters are less than the threshold in a single
            iteration.
        eps_lap: The threshold to be used as convergence criterion for the
            state partition function. Convergence is assumed if the state
            partition function changes less than the threshold on all states
            in a single iteration.
        eps_svf: The threshold to be used as convergence criterion for the
            expected state-visitation frequency. Convergence is assumed if
            the expected state visitation frequency changes less than the
            threshold on all states in a single iteration.
    """
    n_states, _, n_actions = p_transition.shape
    _, n_features = features.shape

    # compute static properties from trajectories
    e_features = feature_expectation_from_trajectories(features, trajectories)
    p_initial = initial_probabilities_from_trajectories(n_states, trajectories)

    # basic gradient descent
    theta = init(n_features)
    delta = np.inf

    optim.reset(theta)
    step_cnt = 0
    while delta > eps:
        theta_old = theta.copy()
        step_cnt =+ 1 
        # compute per-state reward
        reward = features.dot(theta)

        # compute the gradient
        e_svf = compute_expected_causal_svf(p_transition, p_initial, terminal, reward, discount,
                                            eps_lap, eps_svf)

        grad = e_features - features.T.dot(e_svf)

        # perform optimization step and compute delta for convergence
        optim.step(grad)
        delta = np.max(np.abs(theta_old - theta))
        print ("step count: {}".format(step_cnt))
        print ("reward delta: {}".format(delta))

    # re-compute per-state reward and return
    return features.dot(theta)
