# -*- coding: utf-8 -*-
"""
This module computes controls for the SOM3 testcase, replicated from the EnergyPlus .idf file.
DOE Reference Building Small Office (new construction)

"""

from simple_pid import PID



def compute(y):
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


    '''
    SOM3
    List of sensors:
    ---HVAC SENSORS
    senTRoom_y  		- Core zone room temperature sensor (K)
    senTRoom[1-4]_y		- Perimeter zone [1 to 4] room temperature sensor (K)
    senRH_y			- Core zone relative humidity
    senRH[1-4]_y		- Perimeter zone [1 to 4] relative humidity
    senHeaPow_y		- Core zone heating coil power demand (W)
    senHeaPow[1-4]		- Perimeter zone [1 to 4] heating coil power demand (W)
    senCCPow_y			- Core zone cooling coil power demand (W)
    senCCPow[1]_y		- Perimeter zone [1 to 4] cooling coil power demand (W)
    senFanPow_y		- Core zone fan power demand (W)
    senFanPow[1-4]		- Perimeter zone [1 to 4] fan power demand (W)
    ---OTHER OUTPUTS
    senTemOA_y			- Outside air temperature, dry bulb, from weather file (K)
    senDay_y			- Day of the week (1 - Monday to 7 - Sunday)
    senHou_y			- Hour of the day (0-23 hours), only whole hours

    '''

    pidHea = PID(0.00005, 100, 300, setpoint=294.15)
    pidHea.output_limits=(0, 1)
    pidHea.sample_time = 0.01

    pidHea1 = PID(0.00005, 100, 300, setpoint=294.15)
    pidHea1.output_limits=(0, 1)
    pidHea1.sample_time = 0.01

    pidHea2 = PID(0.00005, 100, 300, setpoint=294.15)
    pidHea2.output_limits=(0, 1)
    pidHea2.sample_time = 0.01

    pidHea3 = PID(0.00005, 100, 300, setpoint=294.15)
    pidHea3.output_limits=(0, 1)
    pidHea3.sample_time = 0.01

    pidHea4 = PID(0.00005, 100, 300, setpoint=294.15)
    pidHea4.output_limits=(0, 1)
    pidHea4.sample_time = 0.01

    # Schedule #
    weekDayStart = 6.0
    weekDayEnd = 22.0
    saturdayStart = 6.0
    saturdayEnd = 18.0

    # Controller parameters
    lowerSetpointOccupied = 273.15+21
    upperSetpointOccupied = 273.15+24
    lowerSetpointNonOccupied = 273.15+15.6
    upperSetpointNonOccupied = 273.15+26.7

    minHR = 0.1
    maxHR = 0.9

    minOANonOccupied = 0.0
    minOAOccupied = 1.0

    minVentilationOccupied = 0.7
    minVentilationNonOccupied = 0.01

    # Compute setpoint

    if (y['senDay_y'] <=5 and weekDayStart <= y['senHou_y'] < weekDayEnd) or (y['senDay_y'] ==6 and saturdayStart <= y['senHou_y'] < saturdayEnd):
    	lowerSetpoint = lowerSetpointOccupied
    	upperSetpoint = upperSetpointOccupied
    	minOA = minOAOccupied
    	fanSetpoint = minVentilationOccupied
    else:
    	lowerSetpoint = lowerSetpointNonOccupied
    	upperSetpoint = upperSetpointNonOccupied
    	minOA = minOANonOccupied
    	fanSetpoint = minVentilationNonOccupied

    # Compute controls

        # Heating coils

    if y['senTRoom_y']>lowerSetpoint:
    	oveHCSet = 0.0
    else:
    	oveHCSet = pidHea(y['senTRoom_y'])

    if y['senTRoom1_y']>lowerSetpoint:
    	oveHCSet1 = 0.0
    else:
    	oveHCSet1 = pidHea1(y['senTRoom1_y'])

    if y['senTRoom2_y']>lowerSetpoint:
    	oveHCSet2 = 0.0
    else:
    	oveHCSet2 = pidHea2(y['senTRoom2_y'])

    if y['senTRoom3_y']>lowerSetpoint:
    	oveHCSet3 = 0.0
    else:
    	oveHCSet3 = pidHea3(y['senTRoom3_y'])

    if y['senTRoom4_y']>lowerSetpoint:
    	oveHCSet4 = 0.0
    else:
    	oveHCSet4 = pidHea4(y['senTRoom4_y'])

    	# Cooling coils

    if y['senTRoom_y']<upperSetpoint:
    	oveCC = 0.0
    else:
    	oveCC = 1.0

    if y['senTRoom1_y']<upperSetpoint:
    	oveCC1 = 0.0
    else:
    	oveCC1 = 1.0

    if y['senTRoom2_y']<upperSetpoint:
    	oveCC2 = 0.0
    else:
    	oveCC2 = 1.0

    if y['senTRoom3_y']<upperSetpoint:
    	oveCC3 = 0.0
    else:
    	oveCC3 = 1.0

    if y['senTRoom4_y']<upperSetpoint:
    	oveCC4 = 0.0
    else:
    	oveCC4 = 1.0

    	# Dampers

    oveDam = minOA
    oveDam1 = minOA
    oveDam2 = minOA
    oveDam3 = minOA
    oveDam4 = minOA

       # Fans

    oveVFR = fanSetpoint
    oveVFR1 = fanSetpoint
    oveVFR2 = fanSetpoint
    oveVFR3 = fanSetpoint
    oveVFR4 = fanSetpoint


    u = {'oveHCSet_u':oveHCSet,
         'oveHCSet_activate': 1,
         'oveHCSet1_u':oveHCSet1,
         'oveHCSet1_activate': 1,
         'oveHCSet2_u':oveHCSet2,
         'oveHCSet2_activate': 1,
         'oveHCSet3_u':oveHCSet3,
         'oveHCSet3_activate': 1,
         'oveHCSet4_u':oveHCSet4,
         'oveHCSet4_activate': 1,
         'oveCC_u': oveCC,
         'oveCC_activate': 1,
         'oveCC1_u': oveCC1,
         'oveCC1_activate': 1,
         'oveCC2_u': oveCC2,
         'oveCC2_activate': 1,
         'oveCC3_u': oveCC3,
         'oveCC3_activate': 1,
         'oveCC4_u': oveCC4,
         'oveCC4_activate': 1,
         'oveDSet_u': oveDam,
         'oveDSet_activate': 1,
         'oveDSet1_u': oveDam1,
         'oveDSet1_activate': 1,
         'oveDSet2_u': oveDam2,
         'oveDSet2_activate': 1,
         'oveDSet3_u': oveDam3,
         'oveDSet3_activate': 1,
         'oveDSet4_u': oveDam4,
         'oveDSet4_activate': 1,
         'oveVFRSet_u': oveVFR,
         'oveVFRSet_activate': 1,
         'oveVFRSet1_u': oveVFR1,
         'oveVFRSet1_activate': 1,
         'oveVFRSet2_u': oveVFR2,
         'oveVFRSet2_activate': 1,
         'oveVFRSet3_u': oveVFR3,
         'oveVFRSet3_activate': 1,
         'oveVFRSet4_u': oveVFR4,
         'oveVFRSet4_activate': 1}

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

    u = {'oveHCSet_u':0,
         'oveHCSet_activate': 0,
         'oveHCSet1_u':0,
         'oveHCSet1_activate': 0,
         'oveHCSet2_u':0,
         'oveHCSet2_activate': 0,
         'oveHCSet3_u':0,
         'oveHCSet3_activate': 0,
         'oveHCSet4_u':0,
         'oveHCSet4_activate': 0,
         'oveCC_u': 0,
         'oveCC_activate': 0,
         'oveCC1_u': 0,
         'oveCC1_activate': 0,
         'oveCC2_u': 0,
         'oveCC2_activate': 0,
         'oveCC3_u': 0,
         'oveCC3_activate': 0,
         'oveCC4_u': 0,
         'oveCC4_activate': 0,
         'oveDSet_u': 0,
         'oveDSet_activate': 0,
         'oveDSet1_u': 0,
         'oveDSet1_activate': 0,
         'oveDSet2_u': 0,
         'oveDSet2_activate': 0,
         'oveDSet3_u': 0,
         'oveDSet3_activate': 0,
         'oveDSet4_u': 0,
         'oveDSet4_activate': 0,
         'oveVFRSet_u': 0,
         'oveVFRSet_activate': 0,
         'oveVFRSet1_u': 0,
         'oveVFRSet1_activate': 0,
         'oveVFRSet2_u': 0,
         'oveVFRSet2_activate': 0,
         'oveVFRSet3_u': 0,
         'oveVFRSet3_activate': 0,
         'oveVFRSet4_u': 0,
         'oveVFRSet4_activate': 0}

    return u
