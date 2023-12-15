import pandas as pd; import numpy as np

from utils import pre_process_6

import warnings; import os 
warnings.filterwarnings('ignore')

path = '2_EnergyPlus/6_Buckhead/1_Simulated_Data/'
file_names = os.listdir(path)

# df.to_csv('0_Data/comb_data.csv')

df = pd.DataFrame()

print ("Loading data")
for i in range(len(file_names)):
     data = pd.read_csv(path+str(file_names[i]))
     df_single = pre_process_6(df =data)
     df = pd.concat([df, df_single], ignore_index=True)

print (df.head())
df_n = df

path_save = '2_EnergyPlus/6_Buckhead/2_Combined_Data/'

df.to_csv(path_save+"df.csv")
