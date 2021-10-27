# This started from an example file provided by do-mpc

import matplotlib.pyplot as plt
from casadi.tools import *

from model_parameters import ModelParameters

sys.path.append('../')
import do_mpc
import datetime
import json
import shutil

from pathlib import Path
from template_model import template_model
from template_mpc import template_mpc
from template_simulator import template_simulator
from template_mhe import template_mhe

sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'boptest_client'))
from historian import Historian, Conversions


""" User settings: """
show_animation = True
store_results = True

"""
Get configured do-mpc modules:
"""
model = template_model()
mpc = template_mpc(model)
simulator, boptest_client = template_simulator(model)
if boptest_client is not None:
    results_path = 'results/som3_mpc_boptest'
else:
    results_path = 'results/som3_mpc_statefeedback'

# delete the contents of the results path
if os.path.exists(results_path):
    shutil.rmtree(results_path)
os.makedirs(results_path, exist_ok=True)

historian = Historian(time_step=5)

# Choose one of these estimators
# estimator = template_mhe(model)

# Use the StateFeedback estimator for testing, but it
# is very basic.
estimator = do_mpc.estimator.StateFeedback(model)

"""
Set initial states
"""
np.random.seed(99)

# e = np.ones([model.n_x, 1])
# These default x0's are from a random interval in the simulation.
mp = ModelParameters()
print("here")
print(mp.x0)
print(mp.additional_x_states_inits)
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

# fig, ax, graphics = do_mpc.graphics.default_plot(mpc.data, figsize=(10, 17))
# plt.ion()
#
color = plt.rcParams['axes.prop_cycle'].by_key()['color']

fig, ax = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=(8, 10))

mpc_plot = do_mpc.graphics.Graphics(mpc.data)
mhe_plot = do_mpc.graphics.Graphics(estimator.data)
sim_plot = do_mpc.graphics.Graphics(simulator.data)

axis = 0
ax[axis].set_title('OA Temperature')
mpc_plot.add_line('_tvp', 'TDryBul', ax[axis])

#axis += 1
#ax[axis].set_title('Horizontal Global Irradiance')
#mpc_plot.add_line('_tvp', 'HGloHor', ax[axis])

#axis += 1
#ax[axis].set_title('Occupancy Count')
#mpc_plot.add_line('_tvp', 'occupancy_ratio', ax[axis])

axis += 1
ax[axis].set_title('Power Variables')
mpc_plot.add_line('_u', 'heating_power', ax[axis], color='red')
mpc_plot.add_line('_x', 'cf_heating_power', ax[axis], color='blue')
mpc_plot.add_line('_x', 'heating_power_prev', ax[axis], color='green')
# mpc_plot.add_line('_tvp', 'P1_FanPow', ax[axis], color='blue')
# mpc_plot.add_line('_tvp', 'P1_HeaPow', ax[axis], color='red')
#mpc_plot.add_line('_tvp', 'P1_IntGaiTot', ax[axis], color='green')

#axis += 1
#ax[axis].set_title('Outside Air (m3/s)')
# mpc_plot.add_line('_tvp', 'OAVent', ax[axis])
#mpc_plot.add_line('_tvp', 'OAVent', ax[axis])

axis += 1
ax[axis].set_title('Setpoints and Indoor Temperature')
mpc_plot.add_line('_tvp', 'TSetpoint_Lower', ax[axis], color='red')
mpc_plot.add_line('_tvp', 'TSetpoint_Upper', ax[axis], color='blue')
mpc_plot.add_line('_x', 't_indoor', ax[axis], color='orange')

axis += 1
ax[axis].set_title('Electricity Cost Multiplier')
mpc_plot.add_line('_tvp', 'ElecCost', ax[axis])

# axis += 1
# ax[axis].set_title('Total Power')
# mpc_plot.add_line('_aux', 'total_power', ax[axis])

axis += 1
ax[axis].set_title('Cost Function')
mpc_plot.add_line('_aux', 'cost', ax[axis])

#axis += 1
#ax[axis].set_title('State Matrix X')
#mpc_plot.add_line('_x', 'x', ax[axis])

# ax[4].set_title('Estimated parameters:')

# mhe_plot.add_line('_y', 'y', ax[4])

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
historian.add_point('t_indoor_predicted_after_kalman', 'degC', None, f_conversion=None)

# historian.add_point('T1_Rad', 'degC', 'TRooRad_y')

# 288 5-minute intervals per day
for k in range(288 * 1):
    # for k in range(10):
    current_time = mp.start_time_dt + datetime.timedelta(seconds=(k * 300))
    historian.add_datum('timestamp', current_time.strftime("%Y/%m/%d %H:%M:%S"))
    print(f"{k}: {x0}")

    u0 = mpc.make_step(x0)
    # if u0[0] > 0.05:
    #     print('i am here')

    if boptest_client is None:
        # When not using boptest, then the y_measures is all the states, no need to pull
        # out other states
        y_measured = simulator.make_step(u0)
        historian.add_datum('t_indoor_measured', y_measured[7][0])

        # we are running with no model mismatch, just pass the data back
        x0 = estimator.make_step(y_measured)
        historian.add_datum('t_indoor_predicted', x0[7][0])
    else:
        # y_measured, oa_room = simulator.make_step(u0)
        y_measured, x_next, x0 = simulator.make_step(u0)
        # t + 1

        # the 7th element is the predicted temperature
        # y_pred = mp.c @ x_next[0:x_state_var_cnt] + 273.15
        y_pred = float(x0.master[7])

        x_kalman = x0.master[0:x_state_var_cnt] + mp.K * (y_measured - y_pred)
        y_kalman = mp.c @ x_kalman  # result is in Deg C, and the historian expected it as such.

        # Store to the historian
        historian.add_datum('t_indoor_measured', y_measured)
        historian.add_datum('t_indoor_predicted', y_pred)
        historian.add_datum('t_indoor_predicted_after_kalman', y_kalman)

        # Updating state vars using kalman gain
        # x0.master[0:x_state_var_cnt] = x0.master[0:x_state_var_cnt] + mp.K * (y_measured - y_pred)
        # x0 = np.vstack((
        #     x0.master[0:x_state_var_cnt],
        #    np.array([
        #        [y_measured], # this is of time = t + 1
        #        u0[0],  # THIS IS of time = t
        #        u0[0],  # what to do with this
        #    ])
        # ))

    # save the file every timestep so that you can tail it for a log
    historian.save_csv(results_path, 'historian.csv')

    if show_animation:
        # graphics.plot_results(t_ind=k)
        # graphics.plot_predictions(t_ind=k)
        # graphics.reset_axes()
        mpc_plot.plot_results(t_ind=k)
        mpc_plot.plot_predictions(t_ind=k)
        mpc_plot.reset_axes()
        # ax[3].set_ylim(250, 310)

        # mhe_plot.plot_results()
        # sim_plot.plot_results()
        # mhe_plot.reset_axes()
        # sim_plot.reset_axes()

        plt.show()
        plt.pause(0.005)
        # plt.pause(30)

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



