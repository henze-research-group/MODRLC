import numpy as np;import pandas as pd
from DQN_Agent_test import DQN_Agent
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'openai-gym'))
from boptestGymEnv import BoptestGymEnv
import math
import matplotlib.pyplot as plt


Agent_1 = DQN_Agent(4, 5)
last_ep = 0
Agent_1.model_load_weights("RL_Data_test/02_NN/DQN_" + str(last_ep) + ".h5")  # From 2nd episode
q_value = Agent_1.target_predict_qvalue(np.array([[1,1,1,1]]))
print (q_value)

Agent_1.model_save_weights("RL_Data_test/02_NN/DQN_SAVE_" + str(last_ep) + ".h5")  # From 2nd episode
Agent_1.model_load_weights("RL_Data_test/02_NN/DQN_SAVE_" + str(last_ep) + ".h5")  # From 2nd episode
q_value = Agent_1.target_predict_qvalue(np.array([[1,1,1,1]]))
print (q_value)
