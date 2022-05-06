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
        #'nlpsol_opts': {'ipopt.linear_solver': 'MA27'}
    }

    mpc.set_param(**setup_mpc)

    # this is the cost over the planning horizon.
    mterm = model.aux['cost']  # terminal cost
    lterm = model.aux['cost']  # stage cost

    mpc.set_objective(mterm=mterm, lterm=lterm)

    # Set the tvp_template in the mp class, then assign the tvp_function.
    mp.tvp_template = mpc.get_tvp_template()
    mpc.set_tvp_fun(mp.tvp_fun)

    # set the penalty term for control, we want smooth changes
    mpc.set_rterm(heating_power_core=0.5, 
    heating_power_perimeter1=0.5,
    heating_power_perimeter2=0.5,
    heating_power_perimeter3=0.5,
    heating_power_perimeter4=0.5,
    damper_core=0.5,
    damper_perimeter1=0.5,
    damper_perimeter2=0.5,
    damper_perimeter3=0.5,
    damper_perimeter4=0.5)


    mpc.bounds['lower', '_x', 'x'] = mp.min_x
    mpc.bounds['upper', '_x', 'x'] = mp.max_x

    mpc.bounds['lower', '_u', 'heating_power_core'] = mp.min_heating
    mpc.bounds['upper', '_u', 'heating_power_core'] = mp.max_heating
    mpc.bounds['lower', '_u', 'heating_power_perimeter1'] = mp.min_heating
    mpc.bounds['upper', '_u', 'heating_power_perimeter1'] = mp.max_heating
    mpc.bounds['lower', '_u', 'heating_power_perimeter2'] = mp.min_heating
    mpc.bounds['upper', '_u', 'heating_power_perimeter2'] = mp.max_heating
    mpc.bounds['lower', '_u', 'heating_power_perimeter3'] = mp.min_heating
    mpc.bounds['upper', '_u', 'heating_power_perimeter3'] = mp.max_heating
    mpc.bounds['lower', '_u', 'heating_power_perimeter4'] = mp.min_heating
    mpc.bounds['upper', '_u', 'heating_power_perimeter4'] = mp.max_heating
    mpc.bounds['lower', '_u', 'damper_core'] = mp.min_oa_damp
    mpc.bounds['upper', '_u', 'damper_core'] = mp.max_oa_damp
    mpc.bounds['lower', '_u', 'damper_perimeter1'] = mp.min_oa_damp
    mpc.bounds['upper', '_u', 'damper_perimeter1'] = mp.max_oa_damp
    mpc.bounds['lower', '_u', 'damper_perimeter2'] = mp.min_oa_damp
    mpc.bounds['upper', '_u', 'damper_perimeter2'] = mp.max_oa_damp
    mpc.bounds['lower', '_u', 'damper_perimeter3'] = mp.min_oa_damp
    mpc.bounds['upper', '_u', 'damper_perimeter3'] = mp.max_oa_damp
    mpc.bounds['lower', '_u', 'damper_perimeter4'] = mp.min_oa_damp
    mpc.bounds['upper', '_u', 'damper_perimeter4'] = mp.max_oa_damp


    mpc.setup()

    return mpc
