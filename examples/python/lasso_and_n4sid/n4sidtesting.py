{}
import os
import numpy as np
import pprint
import pickle
import matplotlib.dates as mdates
import matplotlib.pyplot as plt



from pathlib import Path


# Version 3

p = Path('.').resolve().parent / 'lasso_and_n4sid' / 'n4sid_v4'

if p.exists():
    a_matrix = np.load(p / 'matrix_A1.npy')
    b_matrix = np.load(p / 'matrix_B1.npy')
    c_matrix = np.load(p / 'matrix_C1.npy')
    d_matrix = np.load(p / 'matrix_D1.npy')
    
display(a_matrix)
display(b_matrix)
_x = np.array([-0.200731])
_u = np.array([270.287,
248.268,
0,
0,
-22.9892
])

print(a_matrix.shape)
print(_x.shape)
    
print(b_matrix.shape)
print(_u.shape)

x_next = a_matrix @ _x + b_matrix @ _u
y_modeled = c_matrix @ _x + d_matrix @ _u

print(f"x_next is {x_next}")
print(f"y_modeled is {y_modeled}")


## Test if the temperature increases with the x's and u's given in the MPC
from collections import deque

# t_dry_bulb,
# h_glo_hor,
# occupancy_ratio,
# t_heat_setpoint - t_indoor,
# t_indoor_1 - t_cool_setpoint,
# t_dry_bulb - t_indoor_1,
# heating_power,
# cooling_power,
# t_indoor_1,
# t_indoor_1 - t_indoor_2,

# construst the x and u matrix
t_init = 0
# _x = results['mpc']['_x', 'x'][t_init]s
_x = np.array([-0.200731])
print(f"The x_matrix init: {_x}")

sims = {}

t_heat_setpoint_range = [283, 283, 283]
heating_range = [1000, 5000, 11000, 20000]
for t_heat_setpoint in t_heat_setpoint_range:
    for heat in heating_range:
        index = f"{t_heat_setpoint}_{heat}"
        sims[index] = {}
        sims[index]["temperature"] = []
        temps = deque([293, 293, 293])

        t_cool_setpoint = 298
        # var to store results

        for t in range(0,30):

        #     _u = np.array([
        #         results['mpc']['_tvp', 'TDryBul'][t][0],
        #         results['mpc']['_tvp', 'HGloHor'][t][0],
        #         results['mpc']['_tvp', 'occupancy_ratio'][t][0],
        #         results['mpc']['_u', 't_heat_setpoint'][t][0] - results['mpc']['_x', 't_indoor'][t][0],
        #         results['mpc']['_x', 't_indoor'][t][0] - results['mpc']['_u', 't_cool_setpoint'][t][0],
        #         results['mpc']['_tvp', 'TDryBul'][t][0] - results['mpc']['_x', 't_indoor_1'][t][0],
        #         results['mpc']['_u', 'heating_power'][t][0],
        #         results['mpc']['_u', 'cooling_power'][t][0],
        #         results['mpc']['_x', 't_indoor_1'][t][0],
        #         results['mpc']['_x', 't_indoor_1'][t][0] - results['mpc']['_x', 't_indoor_2'][t][0],
        #     ])

            t_indoor = temps.popleft()
            t_indoor_1 = temps[0]
            t_indoor_2 = temps[1]

            # force some of these variables as fixed
            _u = np.array([271.92, #Outside Air Temperature 
                           0, # GLobal Horizontal Irradiance  
                          t_heat_setpoint - t_indoor, # heating term,
                          t_indoor - t_cool_setpoint, #cooling term 
                          273 - t_indoor_1   #infiltration term 

            ])


        #     print(_u)
        #     display(_x)
        #     print(a_matrix.shape)
        #     print(_x.shape)

        #     print(b_matrix.shape)
        #     print(_u.shape)
            x_next = a_matrix @ _x + b_matrix @ _u
            y_modeled = c_matrix @ _x + d_matrix @ _u
        #     display(x_next)
        #     display(y_modeled)
            _x = x_next

            temps.append(y_modeled[0])        
            sims[index]["temperature"].append(y_modeled[0])

        #     print(temps)
#             print(f"Indoor air temperature do-mpc: {results['mpc']['_x', 't_indoor'][t][0]:.2f}, y_modeled: {y_modeled[0]:.2f}. H_sp: {t_heat_setpoint} C_sp: {t_cool_setpoint} ")

colors = ['green', 'blue', 'red', 'yellow']
fig = plt.figure(figsize=(15, 10))

for i_1, t_heating_setpoint in enumerate(t_heat_setpoint_range):
    fig.add_subplot(len(t_heat_setpoint_range), 1, i_1+1)
    for i_2, heat in enumerate(heating_range):
        index = f"{t_heat_setpoint}_{heat}"
        plt.plot(sims[index]["temperature"], colors[i_1], label=f"heat@{heat}:sp@{t_heating_setpoint}")

    plt.ylabel('T (K)')
    plt.legend()
#     plt.title('Indoor Temperatures')

plt.xlabel('Time step (5 mins)')