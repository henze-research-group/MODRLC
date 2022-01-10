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
simulator, actb_client = template_simulator(model)
if actb_client is not None:
    results_path = 'results/som3_mpc_boptest'
else:
    results_path = 'results/som3_mpc_statefeedback'

# delete the contents of the results path
if os.path.exists(results_path):
    shutil.rmtree(results_path)
os.makedirs(results_path, exist_ok=True)

historian = Historian(time_step=5)

# Use the StateFeedback estimator for testing, but it
# is very basic.
estimator = do_mpc.estimator.StateFeedback(model)

"""
Set initial states
"""

mp = ModelParameters()

x0 = np.vstack((mp.x0,
                mp.additional_x_states_inits))

print(f"X0 is now this: {x0}")

mpc.x0 = x0
simulator.x0 = x0
estimator.x0 = x0

# Use initial state to set the initial guess.
mpc.set_initial_guess()

if not isinstance(estimator, do_mpc.estimator.StateFeedback):
    estimator.set_initial_guess()

"""
Setup graphic:
"""

color = plt.rcParams['axes.prop_cycle'].by_key()['color']

fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(8, 10))

mpc_plot = do_mpc.graphics.Graphics(mpc.data)
mhe_plot = do_mpc.graphics.Graphics(estimator.data)
sim_plot = do_mpc.graphics.Graphics(simulator.data)

xticks = range(0, int(mp.length) + 6 * 3600, int(6 * 3600))
xlabels = range(0, int(mp.length/3600) + 6, 6)

axis = 0

ax[axis].set_title('Setpoints and Indoor Temperature')
mpc_plot.add_line('_tvp', 'TSetpoint_Lower', ax[axis], color='red')
mpc_plot.add_line('_tvp', 'TSetpoint_Upper', ax[axis], color='red')
mpc_plot.add_line('_x', 't_indoor', ax[axis], color='black')
sim_plot.add_line('_x', 't_indoor', ax[axis], color='blue')
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_yticks(np.arange(mp.min_indoor_t, mp.max_indoor_t, 2))
ax[axis].set_yticklabels(np.around(np.arange(mp.min_indoor_t-273.15, mp.max_indoor_t-273.15, 2)))
ax[axis].set_ylabel('Temperature [C]')
ax[axis].legend(list(map(ax[axis].get_lines().__getitem__, [0, 4, 6])), ['Setpoints', 'Real temperature (spawn)', 'Simulated temperature (MPC)'], loc='lower right')

axis += 1
ax[axis].set_title('Heating coil command')
mpc_plot.add_line('_u', 'heating_power', ax[axis], color='red')
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_yticks(np.arange(0, 1.2, 0.2))
ax[axis].set_yticklabels(np.arange(0, 120, 20))
ax[axis].set_ylabel('Heating coil power [%]')

axis += 1
ax[axis].set_title('Electricity Cost')
mpc_plot.add_line('_tvp', 'ElecCost', ax[axis])
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_ylabel('Cost [$]')

axis += 1
ax[axis].set_title('Cost Function')
mpc_plot.add_line('_aux', 'cost', ax[axis], label='Total cost')
mpc_plot.add_line('_x', 'discost', ax[axis], label='Discomfort cost')
mpc_plot.add_line('_x', 'eleccost', ax[axis], label='Energy cost')
ax[axis].set_xticks(xticks)
ax[axis].set_xticklabels(xlabels)
ax[axis].set_xlabel('Time [hours]')
ax[axis].set_ylabel('Cost [$]')
ax[axis].legend(list(map(ax[axis].get_lines().__getitem__, [0, 2, 4])), ['Total cost', 'Discomfort cost', 'Energy cost'], loc='upper right')

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
historian.add_point('t_indoor_measured', 'degC', 'TRooAir_y', f_conversion=Conversions.deg_k_to_c)
historian.add_point('t_indoor_predicted', 'degC', None, f_conversion=Conversions.deg_k_to_c)

if actb_client is not None:
    historian.add_point('t_indoor_predicted_after_kalman', 'degC', None, f_conversion=None)

for k in range(int(mp.length/mp.time_step)):

    current_time = mp.start_time_dt + datetime.timedelta(seconds=(k * 300))
    historian.add_datum('timestamp', current_time.strftime("%Y/%m/%d %H:%M:%S"))

    u0 = mpc.make_step(simulator._x0)

    if actb_client is None:
        # When not using boptest, then the y_measures is all the states, no need to pull
        # out other states
        y_measured = simulator.make_step(u0)
        historian.add_datum('t_indoor_measured', y_measured[7][0])

        # we are running with no model mismatch, just pass the data back
        x0 = estimator.make_step(y_measured)
        historian.add_datum('t_indoor_predicted', x0[7][0])
    else:
        y_measured, x_next, simulator._x0 = simulator.make_step(u0)

        # the 4th element is the predicted temperature
        y_pred = float(simulator._x0.master[4])

        x_kalman = simulator._x0.master[0:x_state_var_cnt] + mp.K * (y_measured - y_pred)
        y_kalman = mp.c @ x_kalman  # result is in Deg C, and the historian expected it as such.

        # change x0 to be x_kalman
        simulator._x0.master[0:x_state_var_cnt] = x_kalman
        simulator._x0.master[4] = y_measured

        # Store to the historian
        historian.add_datum('t_indoor_measured', y_measured)
        historian.add_datum('t_indoor_predicted', y_pred)
        historian.add_datum('t_indoor_predicted_after_kalman', y_kalman)

    # save the file every timestep so that you can tail it for a log
    historian.save_csv(results_path, 'historian.csv')

    if show_animation:
        mpc_plot.plot_results(t_ind=k)
        mpc_plot.plot_predictions(t_ind=k)
        mpc_plot.reset_axes()

        sim_plot.plot_results(t_ind=k)
        sim_plot.reset_axes()

        plt.show()
        plt.pause(0.005)
        # plt.pause(30)

actb_client.stop()

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