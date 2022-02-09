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
    t_indoor_core = model.set_variable(var_type='_x', var_name='t_indoor_core', shape=(1, 1))
    t_indoor_perimeter1 = model.set_variable(var_type='_x', var_name='t_indoor_perimeter1', shape=(1, 1))
    t_indoor_perimeter2 = model.set_variable(var_type='_x', var_name='t_indoor_perimeter2', shape=(1, 1))
    t_indoor_perimeter3 = model.set_variable(var_type='_x', var_name='t_indoor_perimeter3', shape=(1, 1))
    t_indoor_perimeter4 = model.set_variable(var_type='_x', var_name='t_indoor_perimeter4', shape=(1, 1))
    cf_heating_power_core = model.set_variable(var_type='_x', var_name='cf_heating_power_core', shape=(1, 1))
    cf_heating_power_perimeter1 = model.set_variable(var_type='_x', var_name='cf_heating_power_perimeter1', shape=(1, 1))
    cf_heating_power_perimeter2 = model.set_variable(var_type='_x', var_name='cf_heating_power_perimeter2',
                                                     shape=(1, 1))
    cf_heating_power_perimeter3 = model.set_variable(var_type='_x', var_name='cf_heating_power_perimeter3',
                                                     shape=(1, 1))
    cf_heating_power_perimeter4 = model.set_variable(var_type='_x', var_name='cf_heating_power_perimeter4',
                                                     shape=(1, 1))
    total_demand = model.set_variable(var_type='_x', var_name='total_demand', shape=(1, 1))
    eleccost = model.set_variable(var_type='_x', var_name='eleccost', shape=(1, 1))
    discost = model.set_variable(var_type='_x', var_name='discost', shape=(1, 1))
    violationcost = model.set_variable(var_type='_x', var_name='violationcost', shape=(1, 1))

    # TVP Variables
    for var in mp.variables:
        if var["type"] == "tvp":
            print(f"Creating variable for tvp of {var['local_var_name']}")
            # The vars() allows a local variable to be created using the string.
            globals()[var["local_var_name"]] = model.set_variable(
                var_type='_tvp', var_name=var["var_name"], shape=(1, 1)
            )

    # the control variables, heating_power. Store previous heating power too.
    heating_power_core = model.set_variable(var_type='_u', var_name='heating_power_core', shape=(1, 1))
    heating_power_perimeter1 = model.set_variable(var_type='_u', var_name='heating_power_perimeter1', shape=(1, 1))
    heating_power_perimeter2 = model.set_variable(var_type='_u', var_name='heating_power_perimeter2', shape=(1, 1))
    heating_power_perimeter3 = model.set_variable(var_type='_u', var_name='heating_power_perimeter3', shape=(1, 1))
    heating_power_perimeter4 = model.set_variable(var_type='_u', var_name='heating_power_perimeter4', shape=(1, 1))

    heating_power_prev_core = model.set_variable(var_type='_x', var_name='heating_power_prev_core', shape=(1, 1))
    heating_power_prev_perimeter1 = model.set_variable(var_type='_x', var_name='heating_power_prev_perimeter1', shape=(1, 1))
    heating_power_prev_perimeter2 = model.set_variable(var_type='_x', var_name='heating_power_prev_perimeter2',
                                                       shape=(1, 1))
    heating_power_prev_perimeter3 = model.set_variable(var_type='_x', var_name='heating_power_prev_perimeter3',
                                                       shape=(1, 1))
    heating_power_prev_perimeter4 = model.set_variable(var_type='_x', var_name='heating_power_prev_perimeter4',
                                                       shape=(1, 1))


    u_array = vertcat(
        heating_power_core,
        heating_power_perimeter1,
        heating_power_perimeter2,
        heating_power_perimeter3,
        heating_power_perimeter4,
        t_dry_bulb,  # outdoor dry bulb temperature
        h_glo_hor,  # global horizontal radiation
        occupancy_ratio_core,
        occupancy_ratio_perimeter1,
        occupancy_ratio_perimeter2,
        occupancy_ratio_perimeter3,
        occupancy_ratio_perimeter4
    )

    # LTI equations
    x_next = mp.a @ _x + mp.b @ u_array
    y_modeled = mp.c @ _x + mp.d @ u_array
    model.set_rhs('x', x_next)

    model.set_rhs("t_indoor_core", y_modeled[0][0] + 273.15)
    model.set_rhs("t_indoor_perimeter1", y_modeled[1][0] + 273.15)
    model.set_rhs("t_indoor_perimeter2", y_modeled[2][0] + 273.15)
    model.set_rhs("t_indoor_perimeter3", y_modeled[3][0] + 273.15)
    model.set_rhs("t_indoor_perimeter4", y_modeled[4][0] + 273.15)
    model.set_rhs("cf_heating_power_core", heating_power_core)
    model.set_rhs("cf_heating_power_perimeter1", heating_power_perimeter1)
    model.set_rhs("cf_heating_power_perimeter2", heating_power_perimeter2)
    model.set_rhs("cf_heating_power_perimeter3", heating_power_perimeter3)
    model.set_rhs("cf_heating_power_perimeter4", heating_power_perimeter4)
    # `heating_power_prev` is needed just to provide an optimization variable for the objective function.
    model.set_rhs("heating_power_prev_core", cf_heating_power_core)
    model.set_rhs("heating_power_prev_perimeter1", cf_heating_power_perimeter1)
    model.set_rhs("heating_power_prev_perimeter2", cf_heating_power_perimeter2)
    model.set_rhs("heating_power_prev_perimeter3", cf_heating_power_perimeter3)
    model.set_rhs("heating_power_prev_perimeter4", cf_heating_power_perimeter4)

    # Thermal discomfort
    discomfort_cost = (fmax(t_indoor_core - tsetpoint_upper, 0) ** 2 + fmax(tsetpoint_lower - t_indoor_core, 0) ** 2) + \
                      (fmax(t_indoor_perimeter1 - tsetpoint_upper, 0) ** 2 + fmax(tsetpoint_lower - t_indoor_perimeter1, 0) ** 2) + \
                      (fmax(t_indoor_perimeter2 - tsetpoint_upper, 0) ** 2 + fmax(tsetpoint_lower - t_indoor_perimeter2, 0) ** 2) + \
                      (fmax(t_indoor_perimeter3 - tsetpoint_upper, 0) ** 2 + fmax(tsetpoint_lower - t_indoor_perimeter3, 0) ** 2) + \
                      (fmax(t_indoor_perimeter4 - tsetpoint_upper, 0) ** 2 + fmax(tsetpoint_lower - t_indoor_perimeter4, 0) ** 2)

    energywaste = t_indoor_core - tsetpoint_lower + \
                t_indoor_perimeter1 - tsetpoint_lower + \
                t_indoor_perimeter2 - tsetpoint_lower + \
                t_indoor_perimeter3 - tsetpoint_lower + \
                t_indoor_perimeter4 - tsetpoint_lower

    # Demand limit
    elec_demand_cost = 7.89  # cost per kW

    hvac_power = cf_heating_power_core * 14035 + \
                 cf_heating_power_perimeter1 * 11316 + \
                 cf_heating_power_perimeter2 * 9873 + \
                 cf_heating_power_perimeter3 * 11587 + \
                 cf_heating_power_perimeter4 * 9691

    equipment_power = equipment_gains_core + \
                      equipment_gains_perimeter1 + \
                      equipment_gains_perimeter2 + \
                      equipment_gains_perimeter3 + \
                      equipment_gains_perimeter4

    total_power = (hvac_power + equipment_power)/1000

    dl_violation_cost = (fmax(total_power - tdl, 0) ** 2) * elec_demand_cost #if_else(total_power>tdl, (total_power - tdl)*elec_demand_cost, 0)

    # Cost of electricity

    elec_unit_cost = 0.0589  # cost per kWh
    elec_cost = hvac_power/1000 * elec_unit_cost * mp.time_step / 3600

    # Cost of control - encourage slow adjustments of coil power, which works better with the current model mismatch
    weight_increase = 2
    weight_decrease = 0.1

    control_cost = weight_increase * fmax(cf_heating_power_core - heating_power_prev_core, 0) ** 2 + weight_decrease * fmax(heating_power_prev_core - cf_heating_power_core, 0) ** 2+\
                   weight_increase * fmax(cf_heating_power_perimeter1 - heating_power_prev_perimeter1, 0) ** 2 + weight_decrease * fmax(heating_power_prev_perimeter1 - cf_heating_power_perimeter1, 0) ** 2+ \
                   weight_increase * fmax(cf_heating_power_perimeter2 - heating_power_prev_perimeter2, 0) ** 2 + weight_decrease * fmax(heating_power_prev_perimeter2 - cf_heating_power_perimeter2, 0) ** 2+ \
                   weight_increase * fmax(cf_heating_power_perimeter3 - heating_power_prev_perimeter3, 0) ** 2 + weight_decrease * fmax(heating_power_prev_perimeter3 - cf_heating_power_perimeter3, 0) ** 2+ \
                   weight_increase * fmax(cf_heating_power_perimeter4 - heating_power_prev_perimeter4, 0) ** 2 + weight_decrease * fmax(heating_power_prev_perimeter4 - cf_heating_power_perimeter4, 0) ** 2

    # weighting factors
    w_power = 100
    w_discomfort = 10
    w_control = 2
    w_dlviolation = 0
    w_waste = 1

    # Cost function

    cost_function = w_power * elec_cost + \
                    w_discomfort * discomfort_cost + \
                    w_dlviolation * dl_violation_cost + \
                    w_control * control_cost + \
                    w_waste * energywaste

    model.set_rhs("discost", w_discomfort * discomfort_cost)
    model.set_rhs("eleccost", w_power * elec_cost)
    model.set_rhs("total_demand", total_power)
    model.set_rhs("violationcost", w_dlviolation * dl_violation_cost)
    model.set_expression(expr_name='cost', expr=cost_function)
    model.setup()

    return model
