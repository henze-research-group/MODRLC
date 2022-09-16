# This started from an example file provided by do-mpc

import matplotlib.pyplot as plt
import numpy as np
from casadi.tools import *

from model_parameters import ModelParameters


import do_mpc
import datetime
import json
import shutil

from pathlib import Path
from template_model import template_model
from template_mpc import template_mpc
from template_simulator import template_simulator

sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'actb_client'))
from historian import Historian, Conversions


""" User settings: """
show_animation = True
store_results = True

"""
Get configured do-mpc modules:
"""
model = template_model()
mpc = template_mpc(model)
simulator, actb_client, t_offset = template_simulator(model)#, metamodel='spawnrefsmalloffice')

results_path = '2days/som3_mpc_boptest'
anim_path = 'anim/'
# delete the contents of the results path
if os.path.exists(results_path):
    shutil.rmtree(results_path)
if os.path.exists(anim_path):
    shutil.rmtree(anim_path)
os.makedirs(results_path, exist_ok=True)
os.makedirs(anim_path, exist_ok=True)


historian = Historian(time_step=5)

"""
Set initial states
"""
np.random.seed(99)

# e = np.ones([model.n_x, 1])
# These default x0's are from a random interval in the simulation.
mp = ModelParameters()
x0 = np.vstack((mp.x0,
                mp.additional_x_states_inits))

mpc.x0 = x0
simulator.x0 = x0

# Use initial state to set the initial guess.
mpc.set_initial_guess()

"""
Setup graphic:
"""

color = plt.rcParams['axes.prop_cycle'].by_key()['color']

fig, ax = plt.subplots(nrows=5, ncols=1, figsize=(13, 10))

mpc_plot = do_mpc.graphics.Graphics(mpc.data)
sim_plot = do_mpc.graphics.Graphics(simulator.data)

xticks = range(0, int(mp.length) + 6 * 3600, int(6 * 3600))
xlabels = range(0, int(mp.length/3600) + 6, 6)

axis = 0

#axis += 1
ax[axis].set_title('Setpoints and Indoor Temperature')
mpc_plot.add_line('_tvp', 'TSetpoint_Lower', ax[axis], color='red', label='Setpoint')
mpc_plot.add_line('_tvp', 'TSetpoint_Upper', ax[axis], color='red')
mpc_plot.add_line('_x', 't_indoor_core', ax[axis], label='Core zone', color='black')
#sim_plot.add_line('_x', 't_indoor_core', ax[axis])
mpc_plot.add_line('_x', 't_indoor_perimeter1', ax[axis], label='South zone', color='blue')
mpc_plot.add_line('_x', 't_indoor_perimeter2', ax[axis], label='East zone', color='orange')
mpc_plot.add_line('_x', 't_indoor_perimeter3', ax[axis], label='North zone', color='green')
mpc_plot.add_line('_x', 't_indoor_perimeter4', ax[axis], label='West zone', color='purple')
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_yticks(np.arange(mp.min_indoor_t, mp.max_indoor_t, 2))
ax[axis].set_yticklabels(np.around(np.arange(mp.min_indoor_t-273.15, mp.max_indoor_t-273.15, 2)))
ax[axis].set_ylabel('Temperature [C]')
ax[axis].legend(list(map(ax[axis].get_lines().__getitem__, [0, 4, 6, 8, 10, 12])), ['Setpoints', 'Core zone', 'South perimeter', 'East perimeter', 'North perimeter', 'West perimeter'], bbox_to_anchor=(1.2, 1.), fancybox=True, shadow=True)

axis += 1
ax[axis].set_title('CO2 concentrations')
mpc_plot.add_line('_tvp', 'co2_setpoint_core', ax[axis])

mpc_plot.add_line('_x', 'co2_core', ax[axis])
mpc_plot.add_line('_x', 'co2_perimeter1', ax[axis])
mpc_plot.add_line('_x', 'co2_perimeter2', ax[axis])
mpc_plot.add_line('_x', 'co2_perimeter3', ax[axis])
mpc_plot.add_line('_x', 'co2_perimeter4', ax[axis])
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_ylabel('CO2 concentration [ppm]')
ax[axis].legend(list(map(ax[axis].get_lines().__getitem__, [0, 2, 4, 6, 8, 10])), ['Upper setpoint', 'Core zone', 'South perimeter', 'East perimeter', 'North perimeter', 'West perimeter'], bbox_to_anchor=(1.2, 1.), fancybox=True, shadow=True)


axis += 1
ax[axis].set_title('Heating coil command')
mpc_plot.add_line('_u', 'heating_power_core', ax[axis])
mpc_plot.add_line('_u', 'heating_power_perimeter1', ax[axis])
mpc_plot.add_line('_u', 'heating_power_perimeter2', ax[axis])
mpc_plot.add_line('_u', 'heating_power_perimeter3', ax[axis])
mpc_plot.add_line('_u', 'heating_power_perimeter4', ax[axis])
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_yticks(np.arange(0, 1.2, 0.2))
ax[axis].set_yticklabels(np.arange(0, 120, 20))
ax[axis].set_ylabel('Heating coil power [%]')
ax[axis].legend(list(map(ax[axis].get_lines().__getitem__, [0, 2, 4, 6, 8])), ['Core zone', 'South perimeter', 'East perimeter', 'North perimeter', 'West perimeter'], bbox_to_anchor=(1.2, 1.), fancybox=True, shadow=True)

axis += 1
ax[axis].set_title('OA damper command')
mpc_plot.add_line('_u', 'damper_core', ax[axis])
mpc_plot.add_line('_u', 'damper_perimeter1', ax[axis])
mpc_plot.add_line('_u', 'damper_perimeter2', ax[axis])
mpc_plot.add_line('_u', 'damper_perimeter3', ax[axis])
mpc_plot.add_line('_u', 'damper_perimeter4', ax[axis])
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_yticks(np.arange(0, 1.2, 0.2))
ax[axis].set_yticklabels(np.arange(0, 120, 20))
ax[axis].set_ylabel('OA fraction [%]')
ax[axis].legend(list(map(ax[axis].get_lines().__getitem__, [0, 2, 4, 6, 8])), ['Core zone', 'South perimeter', 'East perimeter', 'North perimeter', 'West perimeter'], bbox_to_anchor=(1.2, 1.), fancybox=True, shadow=True)



# axis += 1
# ax[axis].set_title('Occupancy')
# mpc_plot.add_line('_tvp', 'occupancy_ratio_core', ax[axis])
# mpc_plot.add_line('_tvp', 'occupancy_ratio_perimeter1', ax[axis])
# mpc_plot.add_line('_tvp', 'occupancy_ratio_perimeter2', ax[axis])
# mpc_plot.add_line('_tvp', 'occupancy_ratio_perimeter3', ax[axis])
# mpc_plot.add_line('_tvp', 'occupancy_ratio_perimeter4', ax[axis])
# ax[axis].set_xticks(xticks)
# ax[axis].set_xticklabels(xlabels)
# ax[axis].set_ylabel('Number of people')
# axis += 1
# ax[axis].set_title('Derivatives')
# mpc_plot.add_line('_aux', 'doa', ax[axis], color='red')
# mpc_plot.add_line('_aux', 'dinf', ax[axis], color='blue')
# mpc_plot.add_line('_aux', 'dppl', ax[axis], color='green')
# ax[axis].set_xticks(xticks)
# ax[axis].set_xticklabels(xlabels)
# ax[axis].set_ylabel('Number of people')
# axis += 1
# ax[axis].set_title('Horizontal irradiation')
# mpc_plot.add_line('_tvp', 'HGloHor', ax[axis])
# ax[axis].set_xticks(xticks)
# ax[axis].set_xticklabels(xlabels)
# ax[axis].set_ylabel('Irradiation [W/m2]')
# #ax[axis].legend(list(map(ax[axis].get_lines().__getitem__, [0, 2])), ['Target demand limit', 'Current demand'], loc='upper right')

axis += 1
ax[axis].set_title('Cost Function')
mpc_plot.add_line('_aux', 'cost', ax[axis], label='Total cost')
mpc_plot.add_line('_aux', 'discost', ax[axis], label='Discomfort cost')
mpc_plot.add_line('_aux', 'eleccost', ax[axis], label='Energy cost')
mpc_plot.add_line('_aux', 'iaqcost', ax[axis], label='IAQ cost')
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_xlabel('Time [hours]')
ax[axis].set_ylabel('Cost [$]')
ax[axis].legend(list(map(ax[axis].get_lines().__getitem__, [0, 2, 4, 6])), ['Total cost', 'Discomfort cost', 'Energy cost', 'IAQ Cost'], bbox_to_anchor=(1.2, 1.), fancybox=True, shadow=True)

for ax_i in ax:
    ax_i.axvline(1.0)

fig.tight_layout()
plt.ion()

"""
Run MPC main loop:
"""

# Save off the model order, which is just the state of the A matrix
x_state_var_cnt = mp.a.shape[0]
u0 = np.array([[0]])

# set up the historian data
historian.add_point('timestamp', 'Time', None)
historian.add_point('t_indoor_measured_core', 'degC', 'TRooAirCore_y', f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_core', 'degC', None, f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_after_kalman_core', 'degC', None, f_conversion=None)

historian.add_point('t_indoor_measured_perimeter1', 'degC', 'TRooAirP1_y', f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_perimeter1', 'degC', None, f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_after_kalman_perimeter1', 'degC', None, f_conversion=None)

historian.add_point('t_indoor_measured_perimeter2', 'degC', 'TRooAirP2_y', f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_perimeter2', 'degC', None, f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_after_kalman_perimeter2', 'degC', None, f_conversion=None)

historian.add_point('t_indoor_measured_perimeter3', 'degC', 'TRooAirP3_y', f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_perimeter3', 'degC', None, f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_after_kalman_perimeter3', 'degC', None, f_conversion=None)

historian.add_point('t_indoor_measured_perimeter4', 'degC', 'TRooAirP4_y', f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_perimeter4', 'degC', None, f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted_after_kalman_perimeter4', 'degC', None, f_conversion=None)

historian.add_point('co2_measured_core', 'ppm', 'senPpmCore_y', f_conversion=None)
historian.add_point('co2_predicted_core', 'ppm', None, f_conversion=None)
#historian.add_point('co2_predicted_after_kalman_core', 'ppm', None, f_conversion=None)

historian.add_point('co2_measured_perimeter1', 'ppm', 'senPpmPerimeter1_y', f_conversion=None)
historian.add_point('co2_predicted_perimeter1', 'ppm', None, f_conversion=None)
#historian.add_point('co2_predicted_after_kalman_perimeter1', 'ppm', None, f_conversion=None)

historian.add_point('co2_measured_perimeter2', 'ppm', 'senPpmPerimeter2_y', f_conversion=None)
historian.add_point('co2_predicted_perimeter2', 'ppm', None, f_conversion=None)
#historian.add_point('co2_predicted_after_kalman_perimeter2', 'ppm', None, f_conversion=None)

historian.add_point('co2_measured_perimeter3', 'ppm', 'senPpmPerimeter3_y', f_conversion=None)
historian.add_point('co2_predicted_perimeter3', 'ppm', None, f_conversion=None)
#historian.add_point('co2_predicted_after_kalman_perimeter3', 'ppm', None, f_conversion=None)

historian.add_point('co2_measured_perimeter4', 'ppm', 'senPpmPerimeter4_y', f_conversion=None)
historian.add_point('co2_predicted_perimeter4', 'ppm', None, f_conversion=None)
#historian.add_point('co2_predicted_after_kalman_perimeter4', 'ppm', None, f_conversion=None)

for k in range(int(mp.length/mp.time_step)):

    current_time = mp.start_time_dt + datetime.timedelta(seconds=(k * 300))
    historian.add_datum('timestamp', current_time.strftime("%Y/%m/%d %H:%M:%S"))
    print(f"{k}: {x0}")

    u0 = mpc.make_step(simulator._x0)

    y_measured, x_next, simulator._x0 = simulator.make_step(u0)
    #print(simulator._x0.master)
    #input("Check x0 out!")
    # the 7th element is the predicted temperature
    y_pred = [float(simulator._x0.master[18]),
              float(simulator._x0.master[19]),
              float(simulator._x0.master[20]),
              float(simulator._x0.master[21]),
              float(simulator._x0.master[22]),
              float(simulator._x0.master[23]),
              float(simulator._x0.master[24]),
              float(simulator._x0.master[25]),
              float(simulator._x0.master[26]),
              float(simulator._x0.master[27])]
    print(y_measured, '\n')
    #input(y_pred)
    x_kalman = simulator._x0.master[0:x_state_var_cnt] + mp.K @ [a - b for a, b in zip(y_measured[5:], y_pred[5:])]
    y_kalman = mp.c @ x_kalman  # result is in Deg C, and the historian expected it as such.
    simulator._x0.master[0:x_state_var_cnt] = x_kalman
    simulator._x0.master[x_state_var_cnt:x_state_var_cnt + 5] = y_measured[:5]
    simulator._x0.master[x_state_var_cnt + 5:x_state_var_cnt + 10] = y_kalman + np.array([273.15]*5)#y_measured[5:]##simulator._x0.master[27:32] + np.array([273.15]*5)

    # Store to the historian
    historian.add_datum('t_indoor_measured_core', y_measured[0])
    historian.add_datum('t_indoor_predicted_core', y_pred[0])
    historian.add_datum('t_indoor_predicted_after_kalman_core', y_kalman[0])

    historian.add_datum('t_indoor_measured_perimeter1', y_measured[1])
    historian.add_datum('t_indoor_predicted_perimeter1', y_pred[1])
    historian.add_datum('t_indoor_predicted_after_kalman_perimeter1', y_kalman[1])

    historian.add_datum('t_indoor_measured_perimeter2', y_measured[2])
    historian.add_datum('t_indoor_predicted_perimeter2', y_pred[2])
    historian.add_datum('t_indoor_predicted_after_kalman_perimeter2', y_kalman[2])

    historian.add_datum('t_indoor_measured_perimeter3', y_measured[3])
    historian.add_datum('t_indoor_predicted_perimeter3', y_pred[3])
    historian.add_datum('t_indoor_predicted_after_kalman_perimeter3', y_kalman[3])

    historian.add_datum('t_indoor_measured_perimeter4', y_measured[4])
    historian.add_datum('t_indoor_predicted_perimeter4', y_pred[4])
    historian.add_datum('t_indoor_predicted_after_kalman_perimeter4', y_kalman[4])

    historian.add_datum('co2_measured_core', y_measured[5])
    historian.add_datum('co2_predicted_core', y_pred[5])

    historian.add_datum('co2_measured_perimeter1', y_measured[6])
    historian.add_datum('co2_predicted_perimeter1', y_pred[6])

    historian.add_datum('co2_measured_perimeter2', y_measured[7])
    historian.add_datum('co2_predicted_perimeter2', y_pred[7])

    historian.add_datum('co2_measured_perimeter3', y_measured[8])
    historian.add_datum('co2_predicted_perimeter3', y_pred[8])

    historian.add_datum('co2_measured_perimeter4', y_measured[9])
    historian.add_datum('co2_predicted_perimeter4', y_pred[9])
    # save the file every timestep so that you can tail it for a log
    historian.save_csv(results_path, 'historian.csv')

    if show_animation:

        mpc_plot.plot_results(t_ind=k)
        mpc_plot.plot_predictions(t_ind=k)
        mpc_plot.reset_axes()

        sim_plot.plot_results(t_ind=k)
        sim_plot.reset_axes()

        # mhe_plot.plot_results()
        # sim_plot.plot_results()
        # mhe_plot.reset_axes()
        # sim_plot.reset_axes()
        plt.savefig('anim/anim_{}.png'.format(k))
        plt.show()
        plt.pause(0.005)

print(f"Finished. Store results is set to {store_results}")
input('Press any key to save the results and exit. (This will close the graph window as well.)')

# Store results:
if store_results:
    # Fetch KPIs from BOPTEST
    kpis = simulator.return_kpis()
    json.dump(kpis, open(f'{results_path}/kpis.json', 'w'))

    historian.save_csv(results_path, 'historian.csv')

    do_mpc_temp_results = 'do_mpc_temp'
    if os.path.exists(f'results/{do_mpc_temp_results}.pkl'):
        os.remove(f'results/{do_mpc_temp_results}.pkl')

    # do_mpc creates a results folder and puts the results there, so save off
    # then move to the right location.
    do_mpc.data.save_results([mpc], do_mpc_temp_results)
    os.rename(f'results/{do_mpc_temp_results}.pkl', f'{results_path}/do_mpc_results.pkl')



