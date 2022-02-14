import numpy as np; import pandas as pd;


def mem_processor(filename):
    mem_list_1 = pd.read_csv(filename, dtype=object)
    mem_list_1.drop(mem_list_1.columns[0], axis=1, inplace=True)
    mem_list_1['Action'] = mem_list_1['Action'].astype('float')
    mem_list_1['Reward'] = mem_list_1['Reward'].astype('float')
    mem_list_1['States'] = mem_list_1['States'].map(
        lambda x: " ".join((x.strip('[').strip(']').replace("\n", "")).split()))
    mem_list_1['States'] = mem_list_1['States'].map(
        lambda x: np.reshape(np.array(x.split(' '), dtype=np.float32), (1, -1)))
    mem_list_1['Next_State'] = mem_list_1['Next_State'].map(
        lambda x: " ".join((x.strip('[').strip(']').replace("\n", "")).split()))
    mem_list_1['Next_State'] = mem_list_1['Next_State'].map(
        lambda x: np.reshape(np.array(x.split(' '), dtype=np.float32), (1, -1)))

    return mem_list_1