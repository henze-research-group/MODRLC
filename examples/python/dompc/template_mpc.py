# MPC configuration for SOM3 model using N4SID system model (planning model)
from casadi.tools import *

sys.path.append('../')
import do_mpc


def template_mpc(model):
    """
    --------------------------------------------------------------------------
    template_mpc: tuning parameters
    --------------------------------------------------------------------------
    """
    mpc = do_mpc.controller.MPC(model)

    setup_mpc = {
        'n_robust': 0,
        'n_horizon': 7,
        't_step': 0.5,
        'state_discretization': 'discrete',
        'store_full_solution': True,
    }

    mpc.set_param(**setup_mpc)

    mterm = model.aux['cost']
    lterm = model.aux['cost']  # terminal cost

    mpc.set_objective(mterm=mterm, lterm=lterm)
    mpc.set_rterm(u=1e-4)

    # need to determine the ranges for the state space model.
    max_x = np.array([[4.0], [10.0], [4.0], [10.0]])

    mpc.bounds['lower', '_x', 'x'] = -max_x
    mpc.bounds['upper', '_x', 'x'] = max_x

    # u for the example is dim(1,1). Need to determine the ranges.
    mpc.bounds['lower', '_u', 'u'] = -0.5
    mpc.bounds['upper', '_u', 'u'] = 0.5

    mpc.setup()

    return mpc
