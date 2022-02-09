# Model template for do-mpc

# Author: Nicholas Long <https://github.com/nllong>

from casadi.tools import *

import do_mpc
from model_parameters import ModelParameters


def template_model():
    model = do_mpc.model.Model('discrete')

    mp = ModelParameters()

    # States struct (optimization variables):
    # x's shape is the A's num of columns x 1
    _x = model.set_variable(var_type='_x', var_name='x', shape=(mp.a.shape[1], 1))

    # additional state for indoor temperature -- mainly for plotting right now
    t_indoor = model.set_variable(var_type='_x', var_name='t_indoor', shape=(1, 1))
    cf_heating_power = model.set_variable(var_type='_x', var_name='cf_heating_power', shape=(1, 1))
    eleccost = model.set_variable(var_type='_x', var_name='eleccost', shape=(1, 1))
    discost = model.set_variable(var_type='_x', var_name='discost', shape=(1, 1))

    # TVP Variables

    for var in mp.variables:
        if var["type"] == "tvp":
            print(f"Creating variable for tvp of {var['local_var_name']}")
            # The vars() allows a local variable to be created using the string.
            globals()[var["local_var_name"]] = model.set_variable(
                var_type='_tvp', var_name=var["var_name"], shape=(1, 1)
            )

    # the control variables, heating_power. Store previous heating power too.
    heating_power = model.set_variable(var_type='_u', var_name='heating_power', shape=(1, 1))
    heating_power_prev = model.set_variable(var_type='_x', var_name='heating_power_prev', shape=(1, 1))

    # In some editors, the variables will not show as being known, this is because of the
    # globals()[] method above to dynamically create all the variables.

    u_array = vertcat(
        heating_power,  # heating power
        t_dry_bulb,  # outdoor dry bulb temperature
        h_glo_hor,  # global horizontal radiation
        occupancy_ratio,  # number of occupants
    )

    # LTI equations
    x_next = mp.a @ _x + mp.b @ u_array
    y_modeled = mp.c @ _x + mp.d @ u_array
    model.set_rhs('x', x_next)

    model.set_rhs("t_indoor", y_modeled[0][0] + 273.15)
    model.set_rhs("cf_heating_power", heating_power)

    # `heating_power_prev` is needed just to provide an optimization variable for the objective function.
    model.set_rhs("heating_power_prev", cf_heating_power)

    # weighting factors
    w_power = 1
    w_discomfort = 5
    w_coc_increase = 2  # cost of control

    # tsetpoint_upper and tsetpoint_lower are defined in the model_parameters imports and vary with time
    discomfort = (fmax(t_indoor - (tsetpoint_upper), 0) ** 2 + fmax((tsetpoint_lower) - t_indoor, 0) ** 2)
    # energy_cost = total_power * elec_unit_cost
    # demand_cost = elec_demand_cost * (fmax(peak_demand - target_demand_limit, 0) ** 2)
    # cost_function = w_power * cf_heating_power * elec_cost_multiplier_no_dr + \
                    # w_discomfort * discomfort + \
                    # w_coc_increase * fmax(cf_heating_power - heating_power_prev, 0) ** 2

    cost_function = w_power * cf_heating_power * elec_cost + \
                    w_discomfort * discomfort + \
                    w_coc_increase * fmax(cf_heating_power - heating_power_prev, 0) ** 2

    model.set_rhs("discost", w_discomfort * discomfort)
    model.set_rhs("eleccost", w_power * cf_heating_power * elec_cost)

    model.set_expression(expr_name='cost', expr=cost_function)
    model.setup()

    return model
