# N4SID state space model. Built using Sippy.

from casadi.tools import *

from model_parameters import ModelParameters

import do_mpc


def template_model():
    model = do_mpc.model.Model('discrete')
    mp = ModelParameters()

    # States struct (optimization variables):
    # x's shape is the A's num of columns x 1
    _x = model.set_variable(var_type='_x', var_name='x', shape=(mp.a.shape[1], 1))

    # Input struct (optimization variables):
    # u's shape is B's num of columns x 1
    for var in mp.variables:
        if var["type"] == "tvp":
            print(f"Creating variable for tvp of {var['local_var_name']}")
            # The vars() allows a local variable to be created using the string.
            globals()[var["local_var_name"]] = model.set_variable(
                var_type='_tvp', var_name=var["var_name"], shape=(1, 1)
            )

    # all the other variables.
    q_con_flow = model.set_variable(var_type='_p', var_name='QCon_flow', shape=(1, 1))  # convective gains
    q_flow = model.set_variable(var_type='_u', var_name='Q_flow', shape=(1, 1))  # heating delivered to space
    fan_p = model.set_variable(var_type='_p', var_name='fanP', shape=(1, 1))  #
    v_flow_supply = model.set_variable(var_type='_p', var_name='volSenSupV_flow', shape=(1, 1))
    v_flow_oa = model.set_variable(var_type='_p', var_name='volSenOAV_flow', shape=(1, 1))
    room_rel_hum = model.set_variable(var_type='_p', var_name='room_relHum', shape=(1, 1))
    t_supply = model.set_variable(var_type='_p', var_name='T_supply', shape=(1, 1))

    # additional state for indoor temperature
    t_indoor = model.set_variable(var_type='_x', var_name='t_indoor', shape=(1, 1))
    t_indoor_prev = model.set_variable(var_type='_x', var_name='t_indoor_prev', shape=(1, 1))

    # weighting parameters
    # k_comfort_penalty = model.set_variable(var_type='_p', var_name='k_comfort_penalty', shape=(1, 1))
    # w_t = model.set_variable(var_type='_tvp', var_name='w_t', shape=(3, 1))

    # Time-varying parameter for the MHE: Weighting of the measurements (tvp):
    # P_v = model.set_variable(var_type='_tvp', var_name='P_v', shape=(5, 5))

    # Power!
    # how do we make the cost function be a LASSO regression (or any other function?)
    # something like: model.set_expression(expr_name='cost', expr=sum1(_x[1] ** 2))
    # need knowledge of the process variables:
    #    secondary variables on power consumption / demand.
    #    where are the constraints -- on y.
    # Simple polynomial fix between Q_flow to represent power and Tdb of OA.
    total_power = model.set_expression('total_power', 0.9871 * t_dry_bulb ** 2 - 576.53 * t_dry_bulb + 84202)

    # In some editors, the variables will not show as being known, this is because of the
    # globals()[] method above to dynamically create all the variables.
    u_array = vertcat(
        h_dif_hor,
        h_dir_nor,
        h_glo_hor,
        h_hor_ir,
        t_bla_sky,
        t_dry_bulb,
        t_wet_bul,
        win_speed,
        win_dir,
        oa_rel_hum,
        q_con_flow,
        q_flow,
        fan_p,
        v_flow_supply,
        v_flow_oa,
        room_rel_hum,
        t_supply
    )
    x_next = mp.a @ _x + mp.b @ u_array
    model.set_rhs('x', x_next)

    y_modeled = mp.c @ _x + mp.d @ u_array

    # when moving to MHE, then need to set the y_meas function, even thought it will come
    # from BOPTEST.
    # model.set_meas("y_meas", y_modeled, meas_noise=False)

    model.set_rhs("t_indoor", y_modeled)

    # Store the previous indoor temperature - this will be used when we add T(t-1) to the u vector.
    model.set_rhs("t_indoor_prev", t_indoor)

    # Economic MPC
    # Each term is multiplier * max(value - threshold, 0) ** order
    #       multiplier is weighting factor (kappa, etc)
    #       order can be 1, 2, ...
    #       value is temperature, energy, PMV
    # penalty = m_discomfort * max(temp - temp_bound, 0) ^ discomfort_order +
    #           m_energy * max(energy - energy_budget, 0) ^ energy_order +
    #           m_energy_cost * max(energy_cost - cost_budget, 0) ^ energy_cost_order +
    #           m_demand * max(peak_demand - target_demand_limit, 0) ^ demand_order
    # cost_function = power * r_t + penalty
    tsetpoint_upper = 25 + 273
    tsetpoint_lower = 20 + 273
    elec_unit_cost = 0.05
    discomfort = (fmax(t_indoor - tsetpoint_upper, 0) ** 2 + fmax(tsetpoint_lower - t_indoor, 0) ** 2)
    energy_consumption = 0
    energy_cost = total_power * elec_unit_cost
    demand = 0
    cost_function = discomfort + energy_cost
    model.set_expression(expr_name='cost', expr=cost_function)

    model.setup()

    return model
