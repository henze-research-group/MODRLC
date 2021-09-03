# This started from an example file provided by do-mpc

import copy
import matplotlib.pyplot as plt
from casadi.tools import *

from model_parameters import ModelParameters

sys.path.append('../')
import do_mpc

from template_model import template_model
from template_mpc import template_mpc
from template_simulator import template_simulator
from template_mhe import template_mhe

""" User settings: """
show_animation = True
store_results = True

"""
Get configured do-mpc modules:
"""
model = template_model()
mpc = template_mpc(model)
simulator, boptest_client = template_simulator(model)

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

# x0 = np.array([
#     [-3.92236858e-01], [-7.88940004e+00], [-5.34412096e+00], [2.21526326e-01], [2.70893994e-01], [1.47842629e-01], [-2.73510110e-02],
#     [293], # indoor temperature
# ])
# x0 = np.array([[-0.8227],
#                [-0.0350391],
#                [-0.0059108],
#                [293],  # indoor temp
#                [293],  # prev indoor temp
#                [293],  # prev prev indoor temp
#                ])
# x0 = np.random.uniform(-3 * e, 3 * e)  # Values between +3 and +3 for all states
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

fig, ax = plt.subplots(nrows=9, ncols=1, sharex=True, figsize=(8, 10))

mpc_plot = do_mpc.graphics.Graphics(mpc.data)
mhe_plot = do_mpc.graphics.Graphics(estimator.data)
sim_plot = do_mpc.graphics.Graphics(simulator.data)

axis = 0
ax[axis].set_title('OA Temperature')
mpc_plot.add_line('_tvp', 'TDryBul', ax[axis])

axis += 1
ax[axis].set_title('Horizontal Global Irradiance')
mpc_plot.add_line('_tvp', 'HGloHor', ax[axis])

axis += 1
ax[axis].set_title('Occupancy Count')
mpc_plot.add_line('_tvp', 'occupancy_ratio', ax[axis])

axis += 1
ax[axis].set_title('Power Variables')
mpc_plot.add_line('_u', 'heating_power', ax[axis], color='red')
# mpc_plot.add_line('_tvp', 'P1_FanPow', ax[axis], color='blue')
# mpc_plot.add_line('_tvp', 'P1_HeaPow', ax[axis], color='red')
mpc_plot.add_line('_tvp', 'P1_IntGaiTot', ax[axis], color='green')

axis += 1
ax[axis].set_title('Outside Air (m3/s)')
# mpc_plot.add_line('_tvp', 'OAVent', ax[axis])
mpc_plot.add_line('_tvp', 'OAVent', ax[axis])

axis += 1
ax[axis].set_title('Setpoints and Indoor Temperature')
mpc_plot.add_line('_tvp', 'TSetpoint_Lower', ax[axis], color='red')
mpc_plot.add_line('_tvp', 'TSetpoint_Upper', ax[axis], color='blue')
mpc_plot.add_line('_x', 't_indoor', ax[axis], color='green')

axis += 1
ax[axis].set_title('Electricity Cost Multiplier')
mpc_plot.add_line('_tvp', 'ElecCost', ax[axis])

# axis += 1
# ax[axis].set_title('Total Power')
# mpc_plot.add_line('_aux', 'total_power', ax[axis])

axis += 1
ax[axis].set_title('Cost Function')
mpc_plot.add_line('_aux', 'cost', ax[axis])

axis += 1
ax[axis].set_title('State Matrix X')
mpc_plot.add_line('_x', 'x', ax[axis])

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
# u0 = mpc.make_step(x0)

# 288 5-minute intervals per day
for k in range(288 * 2):
    # for k in range(10):
    # print(f"{k}: {x0}")
    u0 = mpc.make_step(x0)
    if u0 > 0:
        print('wait here')

    if boptest_client is None:
        # When not using boptest, then the y_measures is all the states, no need to pull
        # out other states
        y_measured = simulator.make_step(u0)
        # we are running with no model mismatch, just pass the data back
        x0 = estimator.make_step(y_measured)
    else:
        # y_measured, oa_room = simulator.make_step(u0)
        y_measured = simulator.make_step(u0)

        # Updating state vars using kalman gain
        y_pred = mp.c @ x0[0:x_state_var_cnt] + 273
        x_next = copy.copy(x0)
        x_next[0:x_state_var_cnt] = x0[0:x_state_var_cnt] + mp.K * (y_measured - y_pred)
        x0 = np.vstack((
            x_next[0:x_state_var_cnt],
            np.array([
                [y_measured],
                u0[0],
                # [oa_room],
            ])
        ))



    # print(x0)

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
input('Press any key to exit.')

# Store results:
if store_results:
    if not isinstance(estimator, do_mpc.estimator.StateFeedback):
        filename = 'som3_mpc_mhe'
    else:
        filename = 'som3_mpc_stateestimator'

    do_mpc.data.save_results([mpc], filename)
