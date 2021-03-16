# MPC configuration for SOM3 model using N4SID system model (planning model)
from casadi.tools import *
from functools import partial
from template_model import ModelParameters

sys.path.append('../')
import do_mpc


def template_mpc(model):
    """
    --------------------------------------------------------------------------
    template_mpc: tuning parameters
    --------------------------------------------------------------------------
    """
    mpc = do_mpc.controller.MPC(model)
    mp = ModelParameters()

    setup_mpc = {
        'n_robust': 0,
        'n_horizon': mp.n_horizon,
        't_step': mp.time_step,
        'state_discretization': 'discrete',
        'store_full_solution': True,
    }

    mpc.set_param(**setup_mpc)

    # this is the cost over the planning horizon.
    mterm = model.aux['cost']  # terminal cost
    lterm = model.aux['cost']  # stage cost

    mpc.set_objective(mterm=mterm, lterm=lterm)

    # Set the tvp_template in the mp class, then assign the tvp_function.
    mp.tvp_template = mpc.get_tvp_template()
    mpc.set_tvp_fun(mp.tvp_fun)

    # mpc.set_rterm(u=1e-4)

    # need to determine the ranges for the state space model.
    mpc.bounds['lower', '_x', 'x'] = mp.min_x
    mpc.bounds['upper', '_x', 'x'] = mp.max_x

    # u for the example is dim(1,1). Need to determine the ranges.
    # mpc.bounds['lower', '_u', 'Var1'] = 200
    # mpc.bounds['upper', '_u', 'Var1'] = 300

    mpc.setup()

    return mpc
