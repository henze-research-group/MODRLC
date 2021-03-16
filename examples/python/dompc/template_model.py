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
            # The vars() allows a local variable to be created using the string.
            print(f"Creating variable for tvp of {var['local_var_name']}")
            globals()[var["local_var_name"]] = model.set_variable(
                var_type='_tvp', var_name=var["var_name"], shape=(1, 1)
            )

    # all the other variables.
    q_con_flow = model.set_variable(var_type='_u', var_name='QCon_flow', shape=(1, 1))
    q_flow = model.set_variable(var_type='_u', var_name='Q_flow', shape=(1, 1))
    fan_p = model.set_variable(var_type='_u', var_name='fanP', shape=(1, 1))
    v_flow_supply = model.set_variable(var_type='_u', var_name='volSenSupV_flow', shape=(1, 1))
    v_flow_oa = model.set_variable(var_type='_u', var_name='volSenOAV_flow', shape=(1, 1))
    room_rel_hum = model.set_variable(var_type='_u', var_name='room_relHum', shape=(1, 1))
    t_supply = model.set_variable(var_type='_u', var_name='T_supply', shape=(1, 1))

    # Time-varying parameter for the MHE: Weighting of the measurements (tvp):
    # P_v = model.set_variable(var_type='_tvp', var_name='P_v', shape=(5, 5))

    # Set expression. These can be used in the cost function, as non-linear constraints
    # or just to monitor another output.

    # how do we make the cost function be a LASSO regression (or any other function?)
    # something like: model.set_expression(expr_name='cost', expr=sum1(_x[1] ** 2))
    # need knowledge of the process variables:
    #    secondary variables on power consumption / demand.
    #    where are the constraints -- on y.

    # assume fixed t setpoint of 22
    model.set_expression(expr_name='cost', expr=sum1(_x ** 2))

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

    # y_exp = mp.c @ _x + mp.d @ u_array
    # model.set_meas('y_meas', y_exp)

    model.setup()

    return model
