# -*- coding: utf-8 -*-
"""
This module implements a simple P controller.

"""

from simple_pid import PID
pid = PID(0.00005, 100, 300, setpoint=294.15)
pid.output_limits=(0, 100)
pid.sample_time = 0.01

def compute_control(y):
    '''Compute the control input from the measurement.

    Parameters
    ----------
    y : dict
        Contains the current values of the measurements.
        {<measurement_name>:<measurement_value>}

    Returns
    -------
    u : dict
        Defines the control input to be used for the next step.
        {<input_name> : <input_value>}

    '''

    # Controller parameters
    LowerSetp = 273.15+20
    UpperSetp = 273.15+23
    k_p = 2000

    # Compute control
    if y['senTRoom1_y']<LowerSetp:
        e = LowerSetp - y['senTRoom1_y']
    elif y['senTRoom1_y']>UpperSetp:
        e = UpperSetp - y['senTRoom1_y']
    else:
        e = 0

    if y['senTRoom1_y']-294.15>0:
    	value = 0.0
    else:
    	value = pid(y['senTRoom1_y'])/100
    if y['senTRoom2_y']-294.15>0:
    	value2 = 0.0
    else:
    	value2 = pid(y['senTRoom2_y'])/100
    if y['senTRoom3_y']-294.15>0:
    	value3 = 0.0
    else:
    	value3 = pid(y['senTRoom3_y'])/100
    if y['senTRoom4_y']-294.15>0:
    	value4 = 0.0
    else:
    	value4 = pid(y['senTRoom4_y'])/100
    if y['senTRoom5_y']-294.15>0:
    	value5 = 0.0
    else:
    	value5 = pid(y['senTRoom5_y'])/100
    u = {'oveHCSet1_u':value,
         'oveHCSet1_activate': 1,
         'oveHCSet2_u':value2,
         'oveHCSet2_activate': 1,
         'oveHCSet3_u':value3,
         'oveHCSet3_activate': 1,
         'oveHCSet4_u':value4,
         'oveHCSet4_activate': 1,
         'oveHCSet5_u':value5,
         'oveHCSet5_activate': 1,
         }
    return u

def initialize():
    '''Initialize the control input u.

    Parameters
    ----------
    None

    Returns
    -------
    u : dict
        Defines the control input to be used for the next step.
        {<input_name> : <input_value>}

    '''

    u = {'oveHCSet1_u':0,
         'oveHCSet1_activate': 1,
         'oveHCSet2_u':0,
         'oveHCSet2_activate': 1,
         'oveHCSet3_u':0,
         'oveHCSet3_activate': 1,
         'oveHCSet4_u':0,
         'oveHCSet4_activate': 1,
         'oveHCSet5_u':0,
         'oveHCSet5_activate': 1}

    return u
