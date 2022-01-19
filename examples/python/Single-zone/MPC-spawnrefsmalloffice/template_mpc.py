# MPC configuration for SOM3 model using N4SID system model (planning model)

from casadi.tools import *

from template_model import ModelParameters

sys.path.append('../../')
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
    # p_template_mpc = mpc.get_p_template(n_combinations=2)
    # def p_fun_mpc(t_now):
    #     # since this is robust MPC, then you have to set up combinations of parameters for
    #     # MPC, which are each evaluated. Only pick one for now.
    #
    #     # QCon_flow, fanP, volSenSupV_flow , volSenOAV_flow, room_relHum, T_supply
    #     p_template_mpc['_p', 0] = np.array([1500, 250, 0.40, 0.0009, 0.50, 295])
    #     p_template_mpc['_p', 1] = np.array([1200, 150, 0.40, 0.0100, 0.50, 298])
    #     return p_template_mpc
    # mpc.set_p_fun(p_fun_mpc)

    # set the penalty term
    # mpc.set_rterm(T_supply=1e-4, Q_flow=1e-4, fanP=1e-4, volSenSupV_flow=1e-4, volSenOAV_flow=1e-4, room_relHum=1e-4)
    mpc.set_rterm(heating_power=1e-8)  # cooling_power=1e-4) fan_power=1e-4,

    mpc.bounds['lower', '_x', 'x'] = mp.min_x
    mpc.bounds['upper', '_x', 'x'] = mp.max_x

    # mpc.bounds['lower', '_x', 't_indoor'] = mp.min_indoor_t
    # mpc.bounds['lower', '_x', 't_indoor'] = mp.max_indoor_t

    # u for the example is dim(1,1). Need to determine the ranges.
    # mpc.bounds['lower', '_u', 'oa_vent'] = 0.01
    # mpc.bounds['upper', '_u', 'oa_vent'] = 0.175
    # mpc.bounds['lower', '_u', 'fan_power'] = mp.min_fan_power
    # mpc.bounds['upper', '_u', 'fan_power'] = mp.max_fan_power
    mpc.bounds['lower', '_u', 'heating_power'] = mp.min_heating
    mpc.bounds['upper', '_u', 'heating_power'] = mp.max_heating
    # mpc.bounds['lower', '_u', 'cooling_power'] = mp.min_cooling
    # mpc.bounds['upper', '_u', 'cooling_power'] = mp.max_cooling

    mpc.setup()

    return mpc
