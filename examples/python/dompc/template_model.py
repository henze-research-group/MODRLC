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
    # additional state for indoor temperature -- mainly for plotting right now
    t_indoor = model.set_variable(var_type='_x', var_name='t_indoor', shape=(1, 1))
    # t_indoor_1 = model.set_variable(var_type='_x', var_name='t_indoor_1', shape=(1, 1))
    # t_indoor_2 = model.set_variable(var_type='_x', var_name='t_indoor_2', shape=(1, 1))

    # TVP Variables
    for var in mp.variables:
        if var["type"] == "tvp":
            print(f"Creating variable for tvp of {var['local_var_name']}")
            # The vars() allows a local variable to be created using the string.
            globals()[var["local_var_name"]] = model.set_variable(
                var_type='_tvp', var_name=var["var_name"], shape=(1, 1)
            )

    # the control variables
    heating_power = model.set_variable(var_type='_u', var_name='heating_power', shape=(1, 1))
    fan_power = model.set_variable(var_type='_u', var_name='fan_power', shape=(1, 1))
    # heating_power = model.set_variable(var_type='_u', var_name='heating_power', shape=(1, 1))
    # cooling_power = model.set_variable(var_type='_u', var_name='cooling_power', shape=(1, 1))

    # weighting parameters
    # k_comfort_penalty = model.set_variable(var_type='_p', var_name='k_comfort_penalty', shape=(1, 1))
    # w_t = model.set_variable(var_type='_tvp', var_name='w_t', shape=(3, 1))
    # DR Time
    w_t = [0.7, 0.2, 0.1]
    # non-DR time
    w_t = [0.0, 0.5, 0.5]

    # Power!
    # how do we make the cost function be a LASSO regression (or any other function?)
    # something like: model.set_expression(expr_name='cost', expr=sum1(_x[1] ** 2))
    # need knowledge of the process variables:
    #    secondary variables on power consumption / demand.
    #    where are the constraints -- on y.
    # Simple polynomial fix between Q_flow to represent power and Tdb of OA. Not that this
    # formulation will not work with a peak demand shedding event since there is no time of day
    # or other variable to reduce total_power other than t_dry_bulb.
    total_power = model.set_expression('total_power', 0.9871 * t_dry_bulb ** 2 - 576.53 * t_dry_bulb + 84202)
    peak_demand = 0  # have to always initialize variable in this case before sending to Casadi. However,
                     # This probably needs to be a state variable if we are constantly looking at the previous peak.
    peak_demand = model.set_expression('peak_demand', fmax(total_power, peak_demand))

    # In some editors, the variables will not show as being known, this is because of the
    # globals()[] method above to dynamically create all the variables.
    # u_array = vertcat(
    #     t_dry_bulb,
    #     h_glo_hor,
    #     t_indoor_1,
    #     t_heat_setpoint - t_indoor_1,
    #     heating_power,
    #     cooling_power,
    #     t_indoor_1 - t_cool_setpoint,
    #     occupancy_ratio,
    #     t_indoor_1 - t_indoor_2,
    #     t_dry_bulb - t_indoor_1,
    # )
    # u_array = vertcat(
    #     t_dry_bulb,
    #     h_glo_hor,
    #     t_heat_setpoint - t_indoor,
    #     t_indoor - t_cool_setpoint,
    #     t_dry_bulb - t_indoor_1,
    # )
    u_array = vertcat(
        t_dry_bulb,
        h_glo_hor,
        5,  # number of occupants
        500,  # internal gains convective flow
        heating_power,
        fan_power,
        0.175     # OA volumetric flow
        )

    # _u = np.array([273, # T_OA (K)  - freezing outside
    #                0,  # Horizontal Global Irradiance (W)
    #                0,  # No occupants [0 - 6]
    #                1000,  # Internal gains convective flow (W), ?  [0 - 3000]
    #                heating_power, # Heating Power (W), [0 - 6000]
    #                500,  # Fan Power (W), ? [0 - 500]
    #                0.175,    # OA Volumetric flow rate (m3/s), [0.01 - 0.175]  # full outside ai
    #                ])

    # LTI equations
    x_next = mp.a @ _x + mp.b @ u_array
    model.set_rhs('x', x_next)
    y_modeled = mp.c @ _x + mp.d @ u_array

    # when moving to MHE, then need to set the y_meas function, even though it will come
    # from BOPTEST. (if using BOPTEST)
    # model.set_meas("t_indoor", y_modeled, meas_noise=False)

    model.set_rhs("t_indoor", y_modeled)
    # Store the previous indoor temperature - this will be used when we add T(t-1) to the x vector.
    # model.set_rhs("t_indoor_1", t_indoor)
    # model.set_rhs("t_indoor_2", t_indoor_1)

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
    elec_unit_cost = 0.0589  # cost per kWh
    elec_demand_cost = 7.89  # cost per kW
    # Need to make these TVPs
    target_demand_limit = 5000
    target_non_dr_limit = 10000

    # tsetpoint_upper and tsetpoint_lower are defined in the model_parameters imports and vary with time
    discomfort = (fmax(t_indoor - tsetpoint_upper, 0) ** 2 + fmax(tsetpoint_lower - t_indoor, 0) ** 2)
    energy_cost = total_power * elec_unit_cost
    demand_cost = elec_demand_cost * (fmax(peak_demand - target_demand_limit, 0) ** 2)
    cost_function = discomfort + energy_cost + demand_cost
    model.set_expression(expr_name='cost', expr=cost_function)
    model.setup()

    return model
