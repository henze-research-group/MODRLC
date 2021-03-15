# This started from an example file provided by do-mpc

import matplotlib.pyplot as plt
from casadi.tools import *

sys.path.append('../')
import do_mpc

from template_model import template_model
from template_mpc import template_mpc
from template_simulator import template_simulator
from template_mhe import template_mhe

""" User settings: """
show_animation = True
store_results = False

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

e = np.ones([model.n_x, 1])
x0 = np.random.uniform(-3 * e, 3 * e)  # Values between +3 and +3 for all states
mpc.x0 = x0
# simulator.x0 = x0
estimator.x0 = x0

# Use initial state to set the initial guess.
mpc.set_initial_guess()
# mhe.set_initial_guess()

"""
Setup graphic:
"""

fig, ax, graphics = do_mpc.graphics.default_plot(mpc.data, figsize=(10, 17))
plt.ion()

# color = plt.rcParams['axes.prop_cycle'].by_key()['color']
#
# fig, ax = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=(10, 9))
#
# mpc_plot = do_mpc.graphics.Graphics(mpc.data)
# mhe_plot = do_mpc.graphics.Graphics(mhe.data)
# sim_plot = do_mpc.graphics.Graphics(simulator.data)
#
# ax[2].set_title('Inputs:')
# mpc_plot.add_line('_u', 'HDifHor', ax[2])
# mpc_plot.add_line('_u', 'HDifHor_2', ax[2])
#
# ax[4].set_title('Estimated parameters:')
# # sim_plot.add_line('_y', 'y', ax[4])
# # mhe_plot.add_line('_y', 'y', ax[4])
#
# for ax_i in ax:
#     ax_i.axvline(1.0)
#
# fig.tight_layout()
# plt.ion()

"""
Run MPC main loop:
"""

for k in range(200):
    u0 = mpc.make_step(x0)
    y_next = simulator.make_step(u0)
    # x0 = mhe.make_step(y_next)
    x0 = estimator.make_step(y_next)


    # raise SystemExit()

    if show_animation:
        graphics.plot_results(t_ind=k)
        graphics.plot_predictions(t_ind=k)
        graphics.reset_axes()
        # mpc_plot.plot_results(t_ind=k)
        # mpc_plot.plot_predictions(t_ind=k)
        # mhe_plot.plot_results()
        # sim_plot.plot_results()
        # mpc_plot.reset_axes()
        # mhe_plot.reset_axes()
        # sim_plot.reset_axes()

        plt.show()
        plt.pause(0.01)


input('Press any key to exit.')

# Store results:
if store_results:
    do_mpc.data.save_results([mpc, simulator], 'oscillating_masses')
