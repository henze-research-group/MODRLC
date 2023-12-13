import numpy as np; import pandas as pd;

''' 01 - Memory processor for fixing memory buffer in proper format for the DQN agent'''

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



''' 02 - Calculate adjacent mean temperature for small office building '''
def calc_mean_temp(state):
    state = np.array(state)
    #print (state)
    Z0_temp = state[0][0]
    Z1_temp = state[0][1]
    Z2_temp = state[0][2]
    Z3_temp = state[0][3]
    Z4_temp = state[0][4]

    adj_temp_Z0 = (Z1_temp +Z2_temp +Z3_temp +Z4_temp)/4
    adj_temp_Z1 = (Z0_temp + Z4_temp + Z2_temp) / 3
    adj_temp_Z2 = (Z0_temp + Z3_temp + Z1_temp) / 3
    adj_temp_Z3 = (Z0_temp + Z4_temp + Z2_temp) / 3
    adj_temp_Z4 = (Z0_temp + Z3_temp + Z1_temp) / 3

    return [adj_temp_Z0,adj_temp_Z1,adj_temp_Z2,adj_temp_Z3,adj_temp_Z4]

'''03 Get current setpoint'''
def get_sp(hour):
  if (hour>=5)&(hour<=22):
      upp_sp = 273.15+24
      low_sp = 273.15+21
  else:
      upp_sp = 273.15+30
      low_sp = 273.15+18
  return [low_sp,upp_sp]


def get_occupancy(hours):
  if (hours>0)&(hours<6):
        occupancy = 2
  elif (hours>=6)&(hours<8):
      occupancy = 12
  elif (hours >= 8) & (hours <18):
      occupancy = 24
  elif (hours >= 18) & (hours <22):
      occupancy = 6
  else:
      occupancy = 2
  
  return occupancy
    

def KPI_df_init():
    kpi_list = ['ener_tot', 'tdis_tot', 'idis_tot', 'cost_tot', 'emis_tot']
    KPI_hist = {key: [] for key in kpi_list}
    KPI_hist['episodes'] = []; KPI_hist['scores'] = []
    KPI_hist['total_cost'] = []; KPI_hist['energy_total_cost'] = []; KPI_hist['tdisc_total_cost'] = []
    KPI_hist['day_no'] = []; KPI_hist['DR_start_time'] = []; KPI_hist['DR_end_time'] = []; KPI_hist['DR_duration'] = []

    return KPI_hist