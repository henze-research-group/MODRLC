# -*- coding: utf-8 -*-
"""
This module implements a simple P controller.

"""

from simple_pid import PID
pid = PID(0.00005, 100, 300, setpoint=294.15)
pid.output_limits=(0, 1)
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

    # Compute control
    if y['senTRoom_y']<LowerSetp:
        e = LowerSetp - y['senTRoom_y']
    elif y['senTRoom_y']>UpperSetp:
        e = UpperSetp - y['senTRoom_y']
    else:
        e = 0

    if y['senTRoom_y']-294.15>0:
    	value = 0.0
    else:
    	value = pid(y['senTRoom_y'])
    cc=0.0
    #if y['senTRoom_y']<LowerSetp:
    #	cc = 0.0
    #elif y['senTRoom_y']>UpperSetp:
    #	cc = 1.0
    #else:
    #	cc = 0.0
    #if y['senTRoom2_y']-294.15>0:
   # 	value2 = 0.0
   # else:
   # 	value2 = pid(y['senTRoom2_y'])/100
   # if y['senTRoom3_y']-294.15>0:
   # 	value3 = 0.0
   # else:
   # 	value3 = pid(y['senTRoom3_y'])/100
   # if y['senTRoom4_y']-294.15>0:
   # 	value4 = 0.0
   # else:
   # 	value4 = pid(y['senTRoom4_y'])/100
   # if y['senTRoom5_y']-294.15>0:
   # 	value5 = 0.0
   # else:
   # 	value5 = pid(y['senTRoom5_y'])/100

    if value != 0.0:
   	 value2 = 0.7
    else:
   	 value2 = 0.7

    u = {'oveHCSet_u':value,
         'oveHCSet_activate': 1,
         'oveVFRSet_u': value2,
         'oveVFRSet_activate': 1,
         'oveCC_u': cc,
         'oveCC_activate': 1}
         #'oveHCSet3_u':value3,
         #'oveHCSet3_activate': 1,
         #'oveHCSet4_u':value4,
         #'oveHCSet4_activate': 1,
         #'oveHCSet5_u':value5,
         #'oveHCSet5_activate': 1,
         #}
    return u, value

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

    u = {'oveHCSet_u':0,
         'oveHCSet_activate': 0,
         'oveVFRSet_u':0,
         'oveVFRSet_activate':0}

    return u
