import os 
import numpy as np; import pandas as pd 
import math
import random
import gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Normal


use_cuda = torch.cuda.is_available()
device   = torch.device("cuda" if use_cuda else "cpu")


class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0
    
    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done
    
    def __len__(self):
        return len(self.buffer)


class ValueNetwork(nn.Module):
    def __init__(self, state_dim, hidden_dim, init_w=3e-3):
        super(ValueNetwork, self).__init__()
        
        self.linear1 = nn.Linear(state_dim, hidden_dim[0])
        self.linear2 = nn.Linear(hidden_dim[0], hidden_dim[1])
        self.linear3 = nn.Linear(hidden_dim[1], hidden_dim[2])
        self.linear4 = nn.Linear(hidden_dim[2], 1)
        
        self.linear4.weight.data.uniform_(-init_w, init_w)
        self.linear4.bias.data.uniform_(-init_w, init_w)
        
    def forward(self, state):
        x = F.relu(self.linear1(state))
        x = F.relu(self.linear2(x))
        x = F.relu(self.linear3(x))
        x = self.linear4(x)
        return x
        
        
class SoftQNetwork(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_size, init_w=3e-3):
        super(SoftQNetwork, self).__init__()
        
        self.linear1 = nn.Linear(num_inputs + num_actions, hidden_size[0])
        self.linear2 = nn.Linear(hidden_size[0], hidden_size[1])
        self.linear3 = nn.Linear(hidden_size[1], hidden_size[2])
        self.linear4 = nn.Linear(hidden_size[2], 1)
        
        self.linear4.weight.data.uniform_(-init_w, init_w)
        self.linear4.bias.data.uniform_(-init_w, init_w)
        
    def forward(self, state, action):
        x = torch.cat([state, action], 1)
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = F.relu(self.linear3(x))
        x = self.linear4(x)
        return x
        
        
class PolicyNetwork(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_size, init_w=3e-3, log_std_min=-20, log_std_max=2):
        super(PolicyNetwork, self).__init__()
        
        self.log_std_min = log_std_min
        self.log_std_max = log_std_max
         
        self.linear1 = nn.Linear(num_inputs, hidden_size[0])
        self.linear2 = nn.Linear(hidden_size[0], hidden_size[1])
        self.linear3 = nn.Linear(hidden_size[1], hidden_size[2])
        
        self.mean_linear = nn.Linear(hidden_size[2], num_actions)

        self.mean_linear.weight.data.uniform_(-init_w, init_w)
        self.mean_linear.bias.data.uniform_(-init_w, init_w)
        
        self.log_std_linear = nn.Linear(hidden_size[2], num_actions)

        self.log_std_linear.weight.data.uniform_(-init_w, init_w)
        self.log_std_linear.bias.data.uniform_(-init_w, init_w)
        
    def forward(self, state):
        x = F.relu(self.linear1(state))
        x = F.relu(self.linear2(x))
        x = F.relu(self.linear3(x))
        
        mean    = self.mean_linear(x)
        log_std = self.log_std_linear(x)
        log_std = torch.clamp(log_std, self.log_std_min, self.log_std_max)
        
        return mean, log_std
    
    def evaluate(self, state, epsilon=1e-6):
        mean, log_std = self.forward(state)
        std = log_std.exp()
                
        normal = Normal(0, 1)
        z      = normal.sample()
        action = torch.tanh(mean+ std*z.to(device))
        log_prob = Normal(mean, std).log_prob(mean+ std*z.to(device)) - torch.log(1 - action.pow(2) + epsilon)
        return action, log_prob, z, mean, log_std        
    
    def get_action(self, state):
        state = torch.FloatTensor(state).unsqueeze(0).to(device)
        mean, log_std = self.forward(state)
        std = log_std.exp()
        
        normal = Normal(0, 1)
        z      = normal.sample().to(device)
        action = torch.tanh(mean + std*z)
        
        action  = action.cpu()#.detach().cpu().numpy()
        return action[0]



class Agent:
    def __init__(self, action_dim, state_dim, hidden_dim,replay_buffer_size,path):
        self.value_net        = ValueNetwork(state_dim, hidden_dim).to(device)
        self.target_value_net = ValueNetwork(state_dim, hidden_dim).to(device)
        self.soft_q_net1 = SoftQNetwork(state_dim, action_dim, hidden_dim).to(device)
        self.soft_q_net2 = SoftQNetwork(state_dim, action_dim, hidden_dim).to(device)
        self.policy_net = PolicyNetwork(state_dim, action_dim, hidden_dim).to(device)
        self.path_NN = path+'02_NN'

        for self.target_param, self.param in zip(self.target_value_net.parameters(), self.value_net.parameters()):
            self.target_param.data.copy_(self.param.data)

        self.value_criterion  = nn.MSELoss()
        self.soft_q_criterion1 = nn.MSELoss()
        self.soft_q_criterion2 = nn.MSELoss()

        self.value_lr  = 0.0005
        self.soft_q_lr = 0.0005
        self.policy_lr = 0.0005
        
        self.value_optimizer  = optim.Adam(self.value_net.parameters(), lr=self.value_lr)
        self.soft_q_optimizer1 = optim.Adam(self.soft_q_net1.parameters(), lr=self.soft_q_lr)
        self.soft_q_optimizer2 = optim.Adam(self.soft_q_net2.parameters(), lr=self.soft_q_lr)
        self.policy_optimizer = optim.Adam(self.policy_net.parameters(), lr=self.policy_lr)

        self.replay_buffer = ReplayBuffer(replay_buffer_size)

    def train(self,batch_size,epochs,gamma=0.99,soft_tau=0.0005):  
        q_value_loss1_l = []
        q_value_loss2_l = []
        value_loss_l = []
        policy_loss_l = []
        for i in range(epochs):
            print ("epochs: {}".format(i))
            state, action, reward, next_state, done = self.replay_buffer.sample(batch_size)
            state      = torch.FloatTensor(state).to(device)
            next_state = torch.FloatTensor(next_state).to(device)
            action     = torch.FloatTensor(action).to(device)
            reward     = torch.FloatTensor(reward).unsqueeze(1).to(device)
            done       = torch.FloatTensor(np.float32(done)).unsqueeze(1).to(device)

            predicted_q_value1 = self.soft_q_net1(state, action)
            predicted_q_value2 = self.soft_q_net2(state, action)
            predicted_value    = self.value_net(state)
            new_action, log_prob, epsilon, mean, log_std = self.policy_net.evaluate(state)
                
                
            # Training Q Function
            target_value = self.target_value_net(next_state)
            target_q_value = reward + (1 - done) * gamma * target_value
            q_value_loss1 = self.soft_q_criterion1(predicted_q_value1, target_q_value.detach())
            q_value_loss2 = self.soft_q_criterion2(predicted_q_value2, target_q_value.detach())   


            self.soft_q_optimizer1.zero_grad()
            q_value_loss1.backward()
            self.soft_q_optimizer1.step()
            self.soft_q_optimizer2.zero_grad()
            q_value_loss2.backward()
            self.soft_q_optimizer2.step()    

            # Training Value Function
            predicted_new_q_value = torch.min(self.soft_q_net1(state, new_action),self.soft_q_net2(state, new_action))
            target_value_func = predicted_new_q_value - log_prob
            value_loss = self.value_criterion(predicted_value, target_value_func.detach())

                
            self.value_optimizer.zero_grad()
            value_loss.backward()
            self.value_optimizer.step()
            # Training Policy Function

            policy_loss = (log_prob - predicted_new_q_value).mean()
            self.policy_optimizer.zero_grad()
            policy_loss.backward()
            self.policy_optimizer.step()

            #track loss 
            q_value_loss1_l.append(q_value_loss1.item())
            q_value_loss2_l.append(q_value_loss2.item())
            value_loss_l.append(value_loss.item())
            # policy_loss_l.append(policy_loss.item())
            
            
            for self.target_param, self.param in zip(self.target_value_net.parameters(), self.value_net.parameters()):
                self.target_param.data.copy_(self.target_param.data * (1.0 - soft_tau) + self.param.data * soft_tau)
    
        return q_value_loss1_l,q_value_loss2_l,value_loss_l,policy_loss_l

    def remember(self,state, action, reward, next_state, done):  
        self.replay_buffer.push(state, action, reward, next_state, done)

    def buffer_mem(self):
        return len(self.replay_buffer)

    def get_action(self,state):
        action = self.policy_net.get_action(state).detach().numpy()
        return action

    def save_models(self,episode):
        torch.save(self.value_net.state_dict(), self.path_NN+'/value_net_'+str(episode)+'.pth')
        torch.save(self.target_value_net.state_dict(), self.path_NN+'/target_value_net_'+str(episode)+'.pth')
        torch.save(self.soft_q_net1.state_dict(), self.path_NN+'/soft_q_net1_'+str(episode)+'.pth')
        torch.save(self.soft_q_net2.state_dict(), self.path_NN+'/soft_q_net2_'+str(episode)+'.pth')
        torch.save(self.policy_net.state_dict(), self.path_NN+'/policy_net_'+str(episode)+'.pth')

    def load_models(self,episode):
        self.value_net.load_state_dict(torch.load(self.path_NN+'/value_net_'+str(episode)+'.pth'))
        self.target_value_net.load_state_dict(torch.load(self.path_NN+'/target_value_net_'+str(episode)+'.pth'))
        self.soft_q_net1.load_state_dict(torch.load(self.path_NN+'/soft_q_net1_'+str(episode)+'.pth'))
        self.soft_q_net2.load_state_dict(torch.load(self.path_NN+'/soft_q_net2_'+str(episode)+'.pth'))
        self.policy_net.load_state_dict(torch.load(self.path_NN+'/policy_net_'+str(episode)+'.pth'))

    def load_data(self,episodes,path):
        file_names = os.listdir(path+'04_Mem/')
        print ("file names: {}".format(file_names))
        for file_name in file_names[0:episodes]:
            df = pd.read_pickle(path+"04_Mem/"+str(file_name))
            print ("loading: {}".format(file_name))
            for i in range(len(df)):
                state = df.iloc[i]['states']
                reward = df.iloc[i]['reward']
                action = df.iloc[i]['action']
                next_state = df.iloc[i]['next_states']
                done = df.iloc[i]['done']
                self.remember(state=state,action=action,reward=reward,next_state=next_state,done=done)
     

