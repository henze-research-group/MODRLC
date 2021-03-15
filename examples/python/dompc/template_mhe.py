# This is just a stub. Need to decide how to use this or kalman filters.

from casadi.tools import *
from template_model import ModelParameters
sys.path.append('../../')
import do_mpc


def template_mhe(model):
    """
    --------------------------------------------------------------------------
    template_mhe: tuning parameters
    --------------------------------------------------------------------------
    """
    mhe = do_mpc.estimator.MHE(model, [])
    mp = ModelParameters()

    setup_mhe = {
        'n_horizon': mp.n_horizon,
        't_step': mp.time_step,
        'store_full_solution': True,
        # 'nl_cons_check_colloc_points': True,
        # 'nlpsol_opts': {'ipopt.linear_solver': 'MA27'},
    }

    mhe.set_param(**setup_mhe)

    # P_v = model.tvp['P_v']

    # P_x is the weighting matrix, which is the size of the X order
    P_x = 1e-4 * np.eye(mp.a.shape[1])
    # P_p = model.p['P_p']

    # no error in the measurement
    P_v = 0 * np.eye(1)

    # Set the default MHE objective by passing the weighting matrices:
    mhe.set_default_objective(P_x, P_v)

    # P_y is listed in the time-varying parameters and must be set.
    # This is more of a proof of concept (P_y is not actually changing over time).
    # We therefore do the following:
    # tvp_template = mhe.get_tvp_template()
    # tvp_template['_tvp', :, 'P_v'] = np.diag(np.array([1, 1, 1, 20, 20]))
    #
    # # Typically, the values would be reset at each call of tvp_fun.
    # # Here we just return the fixed values:
    # def tvp_fun(t_now):
    #     return tvp_template
    #
    # mhe.set_tvp_fun(tvp_fun)

    # Only the non estimated parameters must be passed:
    # p_template_mhe = mhe.get_p_template()
    #
    # def p_fun_mhe(t_now):
    #     p_template_mhe['Theta_2'] = 2.25e-4
    #     p_template_mhe['Theta_3'] = 2.25e-4
    #     # And our previously set P_x:
    #     p_template_mhe['P_p'] = np.eye(1)
    #     return p_template_mhe
    #
    # mhe.set_p_fun(p_fun_mhe)


    # Measurement function:
    y_template = mhe.get_y_template()

    def y_fun(t_now):
        n_steps = min(mhe.data._y.shape[0], mhe.n_horizon)
        for k in range(-n_steps, 0):
            y_template['y_meas', k] = mhe.data._y[k]

        return y_template

    mhe.set_y_fun(y_fun)

    tvp_template = mhe.get_tvp_template()
    def tvp_fun(t_now):
        print(t_now)
        print(tvp_template)
        return tvp_template

    mhe.set_tvp_fun(tvp_fun)

    # mhe.bounds['lower', '_u', 'phi_m_set'] = -5
    # mhe.bounds['upper', '_u', 'phi_m_set'] = 5

    # mhe.bounds['lower', '_x', 'dphi'] = -6
    # mhe.bounds['upper', '_x', 'dphi'] = 6

    # Instead of setting bound like this:
    # mhe.bounds['lower','_p_est', 'Theta_1'] = 1e-5
    # mhe.bounds['upper','_p_est', 'Theta_1'] = 1e-3

    # The MHE also supports nonlinear constraints (here they are still linear however) ...
    # mhe.set_nl_cons('p_est_lb', -mhe._p_est['Theta_1'] + 1e-5, 0)
    # mhe.set_nl_cons('p_est_ub', mhe._p_est['Theta_1'] - 1e-3, 0)

    mhe.setup()

    return mhe
