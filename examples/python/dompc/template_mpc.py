# MPC configuration for SOM3 model using N4SID system model (planning model)
from casadi.tools import *

from template_model import ModelParameters
import numpy as np

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

    # Testing the _parameter configuration
    p_template_mpc = mpc.get_p_template(n_combinations=2)
    def p_fun_mpc(t_now):
        # since this is robust MPC, then you have to set up combinations of parameters for
        # MPC, which are each evaluated. Only pick one for now.

        # QCon_flow, fanP, volSenSupV_flow , volSenOAV_flow, room_relHum, T_supply
        p_template_mpc['_p', 0] = np.array([1500, 250, 0.40, 0.0009, 0.50, 295])
        p_template_mpc['_p', 1] = np.array([1200, 150, 0.40, 0.0100, 0.50, 298])
        return p_template_mpc
    mpc.set_p_fun(p_fun_mpc)

    # set the penalty term
    # mpc.set_rterm(T_supply=1e-4, Q_flow=1e-4, fanP=1e-4, volSenSupV_flow=1e-4, volSenOAV_flow=1e-4, room_relHum=1e-4)
    mpc.set_rterm(Q_flow=1e-4)

    mpc.bounds['lower', '_x', 'x'] = mp.min_x
    mpc.bounds['upper', '_x', 'x'] = mp.max_x

    # u for the example is dim(1,1). Need to determine the ranges.
    # mpc.bounds['lower', '_u', 'T_supply'] = 275
    # mpc.bounds['upper', '_u', 'T_supply'] = 315
    mpc.bounds['lower', '_u', 'Q_flow'] = 0
    mpc.bounds['upper', '_u', 'Q_flow'] = 30000
    # mpc.bounds['lower', '_u', 'fanP'] = 0
    # mpc.bounds['upper', '_u', 'fanP'] = 550
    # mpc.bounds['lower', '_u', 'volSenSupV_flow'] = 0
    # mpc.bounds['upper', '_u', 'volSenSupV_flow'] = 0.5
    # mpc.bounds['lower', '_u', 'volSenOAV_flow'] = 0
    # mpc.bounds['upper', '_u', 'volSenOAV_flow'] = 0.5
    # mpc.bounds['lower', '_u', 'room_relHum'] = 0
    # mpc.bounds['upper', '_u', 'room_relHum'] = 1

    mpc.setup()

    return mpc
