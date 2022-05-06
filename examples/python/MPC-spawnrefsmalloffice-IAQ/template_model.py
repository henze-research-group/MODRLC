# Model template for do-mpc

# Author: Nicholas Long <https://github.com/nllong>

from casadi.tools import *
import numpy as np

import do_mpc
from model_parameters import ModelParameters


def template_model():
    model = do_mpc.model.Model('discrete')

    mp = ModelParameters()

    # States struct (optimization variables):
    # x's shape is the A's num of columns x 1
    _x = model.set_variable(var_type='_x', var_name='x', shape=(mp.a.shape[1], 1))

    # additional state for indoor temperature -- mainly for plotting right now
    co2_core = model.set_variable(var_type='_x', var_name='co2_core', shape=(1, 1))
    co2_perimeter1 = model.set_variable(var_type='_x', var_name='co2_perimeter1', shape=(1, 1))
    co2_perimeter2 = model.set_variable(var_type='_x', var_name='co2_perimeter2', shape=(1, 1))
    co2_perimeter3 = model.set_variable(var_type='_x', var_name='co2_perimeter3', shape=(1, 1))
    co2_perimeter4 = model.set_variable(var_type='_x', var_name='co2_perimeter4', shape=(1, 1))

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
    damper_core = model.set_variable(var_type='_u', var_name='damper_core', shape=(1, 1))
    damper_perimeter1 = model.set_variable(var_type='_u', var_name='damper_perimeter1', shape=(1, 1))
    damper_perimeter2 = model.set_variable(var_type='_u', var_name='damper_perimeter2', shape=(1, 1))
    damper_perimeter3 = model.set_variable(var_type='_u', var_name='damper_perimeter3', shape=(1, 1))
    damper_perimeter4 = model.set_variable(var_type='_u', var_name='damper_perimeter4', shape=(1, 1))

    prev_people = model.set_variable(var_type='_x', var_name='prev_people', shape=(5, 1))
    prev_oa = model.set_variable(var_type='_x', var_name='prev_oa', shape=(5, 1))

    u_array = vertcat(
        heating_power_core,
        heating_power_perimeter1,
        heating_power_perimeter2,
        heating_power_perimeter3,
        heating_power_perimeter4,
        damper_core,
        damper_perimeter1,
        damper_perimeter2,
        damper_perimeter3,
        damper_perimeter4,
        t_dry_bulb,  # outdoor dry bulb temperature
        h_glo_hor,  # global horizontal radiation
        occupancy_ratio_core,
        occupancy_ratio_perimeter1,
        occupancy_ratio_perimeter2,
        occupancy_ratio_perimeter3,
        occupancy_ratio_perimeter4
    )

    ppl = vertcat(
        occupancy_ratio_core,
        occupancy_ratio_perimeter1,
        occupancy_ratio_perimeter2,
        occupancy_ratio_perimeter3,
        occupancy_ratio_perimeter4
    )

    damper = vertcat(
        damper_core,
        damper_perimeter1,
        damper_perimeter2,
        damper_perimeter3,
        damper_perimeter4,
    )
    cur_co2 = vertcat(
        co2_core,
        co2_perimeter1,
        co2_perimeter2,
        co2_perimeter3,
        co2_perimeter4,

    )

    # This first order ODE solves the CO2 concentration given the OA fraction and the occupant density
    ppl_next = (ppl - prev_people) / mp.k5.T
    oa_next = (damper - prev_oa) / mp.k6.T

    #- k1 * oavol * (co2 - 397.5) - k2 * (co2 - 397.5) + k3 * ppco2 + k4

    doa = - mp.k1 * oa_next.T * (cur_co2.T - mp.oaco2)
    dinf = - mp.k2 * (cur_co2.T - mp.oaco2)
    dppl = mp.k3 * ppl_next.T
    co2_next = cur_co2.T + doa + dppl + dinf + mp.k4

    model.set_rhs("prev_people", ppl_next)
    model.set_rhs("prev_oa", oa_next.T)
    #model.set_rhs("prev_co2", co2_next)

    model.set_rhs("co2_core", co2_next[0])
    model.set_rhs("co2_perimeter1", co2_next[1])
    model.set_rhs("co2_perimeter2", co2_next[2])
    model.set_rhs("co2_perimeter3", co2_next[3])
    model.set_rhs("co2_perimeter4", co2_next[4]) 

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

    indoor_temps = vertcat(
        t_indoor_core,
        t_indoor_perimeter1,
        t_indoor_perimeter2,
        t_indoor_perimeter3,
        t_indoor_perimeter4
    )

    upperbounds = vertcat(
        tsetpoint_upper,
        tsetpoint_upper,
        tsetpoint_upper,
        tsetpoint_upper,
        tsetpoint_upper
    )

    lowerbounds = vertcat(
        tsetpoint_lower,
        tsetpoint_lower,
        tsetpoint_lower,
        tsetpoint_lower,
        tsetpoint_lower
    )

    indoor_co2 = vertcat(
        co2_core,
        co2_perimeter1,
        co2_perimeter2,
        co2_perimeter3,
        co2_perimeter4

    )

    co2setpoints = vertcat (
        co2_setpoint_core,
        co2_setpoint_perimeter1,
        co2_setpoint_perimeter2,
        co2_setpoint_perimeter3,
        co2_setpoint_perimeter4

    )


    # Thermal discomfort

    discomfort_cost = sum1(fmax(indoor_temps - upperbounds, 0) ** 2 + fmax(lowerbounds - indoor_temps, 0) ** 2)

    iaq_cost = sum1(fmax(indoor_co2 - co2setpoints, 0) ** 2)


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

    # Cost of electricity

    elec_unit_cost = 0.0589  # cost per kWh
    elec_cost = hvac_power/1000 * elec_unit_cost * mp.time_step / 3600

    # weighting factors
    w_power = 1
    w_discomfort = 1
    w_iaq = 0.1

    # Cost function
    cost_function = w_power * elec_cost + \
                    w_discomfort * discomfort_cost + \
                    w_iaq * iaq_cost
    model.set_expression(expr_name='discost', expr=w_discomfort * discomfort_cost)
    model.set_expression(expr_name='eleccost', expr=w_power * elec_cost)
    model.set_expression(expr_name='total_demand', expr=total_power)
    model.set_expression(expr_name='iaqcost', expr=w_iaq * iaq_cost)
    model.set_expression(expr_name='cost', expr=cost_function)
    model.setup()

    return model
