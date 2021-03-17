# This started from an example file provided by do-mpc

import matplotlib.pyplot as plt
from casadi.tools import *

from model_parameters import ModelParameters

sys.path.append('../')
import do_mpc

from template_model import template_model
from template_mpc import template_mpc
from template_simulator import template_simulator

""" User settings: """
show_animation = True
store_results = True

"""
Get configured do-mpc modules:
"""
model = template_model()
mpc = template_mpc(model)
simulator = template_simulator(model)
# mhe = template_mhe(model)

# Use the StateFeedback estimator for testing, but it
# is very basic.
estimator = do_mpc.estimator.StateFeedback(model)

"""
Set initial state
"""
np.random.seed(99)

# e = np.ones([model.n_x, 1])
# These default x0's are from a random interval in the simulation.
x0 = np.array([[-0.91468989], [-0.15824672], [-3.70572322], [2.61228931],
               [-0.09639031], [0.12383332], [0.56911312], [0.75327032],
               [293], # indoor temp
               [293], # prev indoor temp
               ])
# x0 = np.random.uniform(-3 * e, 3 * e)  # Values between +3 and +3 for all states
mpc.x0 = x0
simulator.x0 = x0
# mhe.x0 = x0
estimator.x0 = x0

# Use initial state to set the initial guess.
mpc.set_initial_guess()
# mhe.set_initial_guess()

"""
Setup graphic:
"""

# fig, ax, graphics = do_mpc.graphics.default_plot(mpc.data, figsize=(10, 17))
# plt.ion()
#
color = plt.rcParams['axes.prop_cycle'].by_key()['color']

fig, ax = plt.subplots(nrows=9, ncols=1, sharex=True, figsize=(10, 9))

mpc_plot = do_mpc.graphics.Graphics(mpc.data)
mhe_plot = do_mpc.graphics.Graphics(estimator.data)
sim_plot = do_mpc.graphics.Graphics(simulator.data)

# Setup the plots based on the ModelParameter variables
mp = ModelParameters()
for var in mp.variables:
    # find all of the tvp
    if var["type"] == "tvp":
        if var["plot_axis"] is not None:
            mpc_plot.add_line("_tvp", var["var_name"], ax[var["plot_axis"]])
            # ax[1].legend(
            #     mpc_plot.result_lines['_x', 'phi_2']+mpc_plot.result_lines['_tvp', 'phi_2_set']+mpc_plot.pred_lines['_x', 'phi_2'],
            #     ['Recorded', 'Setpoint', 'Predicted'], title='Disc 2')

ax[0].set_title('Inputs')
# mpc_plot.add_line('_u', 'T_supply', ax[0])
mpc_plot.add_line('_u', 'Q_flow', ax[0])
# mpc_plot.add_line('_u', 'fanP', ax[0])
# mpc_plot.add_line('_u', 'volSenSupV_flow', ax[0])
# mpc_plot.add_line('_u', 'volSenOAV_flow', ax[0])
# mpc_plot.add_line('_u', 'room_relHum', ax[0])

ax[1].set_title('OA Temperatures TVPs')

ax[2].set_title('Irradiance TVPs')

ax[3].set_title('Indoor Air Temperature')
mpc_plot.add_line('_x', 't_indoor', ax[3])
mpc_plot.add_line('_x', 't_indoor_prev', ax[3])

ax[4].set_title('Setpoints TVP')

ax[5].set_title('Elec Cost')

ax[6].set_title('Power')
mpc_plot.add_line('_aux', 'total_power', ax[6])

ax[7].set_title('Cost Function')
mpc_plot.add_line('_aux', 'cost', ax[7])

# ax[4].set_title('Estimated parameters:')

# mhe_plot.add_line('_y', 'y', ax[4])

for ax_i in ax:
    ax_i.axvline(1.0)

fig.tight_layout()
plt.ion()

"""
Run MPC main loop:
"""

# 288 5-minute intervals per day
for k in range(288):
    # for k in range(10):
    u0 = mpc.make_step(x0)
    y_next = simulator.make_step(u0)
    # x0 = mhe.make_step(y_next)
    x0 = estimator.make_step(y_next)

    if show_animation:
        # graphics.plot_results(t_ind=k)
        # graphics.plot_predictions(t_ind=k)
        # graphics.reset_axes()
        mpc_plot.plot_results(t_ind=k)
        mpc_plot.plot_predictions(t_ind=k)
        mpc_plot.reset_axes()
        # mhe_plot.plot_results()
        # sim_plot.plot_results()
        # mhe_plot.reset_axes()
        # sim_plot.reset_axes()

        plt.show()
        plt.pause(0.01)

print(f"Finished. Store results is set to {store_results}")
input('Press any key to exit.')

# Store results:
if store_results:
    do_mpc.data.save_results([mpc], 'som3')
