# MPC configuration for SOM3 model using N4SID system model (planning model)
from casadi.tools import *
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

    mterm = model.aux['cost']
    lterm = model.aux['cost']  # terminal cost

    mpc.set_objective(mterm=mterm, lterm=lterm)
    mpc.set_rterm(u=1e-4)

    # need to determine the ranges for the state space model.
    mpc.bounds['lower', '_x', 'x'] = mp.min_x
    mpc.bounds['upper', '_x', 'x'] = mp.max_x

    # u for the example is dim(1,1). Need to determine the ranges.
    mpc.bounds['lower', '_u', 'u'] = mp.min_u
    mpc.bounds['upper', '_u', 'u'] = mp.max_u

    mpc.setup()

    return mpc
