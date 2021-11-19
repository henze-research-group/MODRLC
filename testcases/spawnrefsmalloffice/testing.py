# -*- coding: utf-8 -*-
"""
This module manages the simulation of SOM3 in BOPTEST. It initializes,
steps and computes controls for the HVAC system.
The testcase docker container must be running before launching this
script.
"""

# GENERAL PACKAGE IMPORT
# ----------------------
import requests
import json, collections
import time as _time
import os

def run(plot=False):
    '''Run test case.

    Parameters
    ----------
    plot : bool, optional
        True to plot timeseries results.
        Default is False.
    customized_kpi_config : string, optional
        The path of the json file which contains the customized kpi information.
        Default is None.

    Returns
    -------
    kpi : dict
        Dictionary of core KPI names and values.
        {kpi_name : value}
    res : dict
        Dictionary of trajectories of inputs and outputs.
    customizedkpis_result: dict
        Dictionary of tracked custom KPI calculations.
        Empty if no customized KPI calculations defined.

    '''
    
    # SETUP TEST CASE
    # ---------------
    # Set URL for testcase
    # url = 'http://127.0.0.1:5000'
    
    url = 'http://0.0.0.0:5000'
    
    # Set simulation parameters
    length = 2 * 365 * 24 * 3600

    step = 7200

    simStartTime = 0
    warmupPeriod = 0
    
    heatingScenario1 = [36 * 24 * 3600, 42 * 24 * 3600] #Feb 5th to Feb 11th
    heatingScenario2 = [316 * 24 * 3600, 322 * 24 * 3600] #Nov 12th to Nov 18th
    coolingScenario1 = [127 * 24 * 3600, 133 * 24 * 3600] #May 7th to May 13th
    coolingScenario2 = [204 * 24 * 3600 , 210 * 24 * 3600] #Jul 23rd to Jul 29th
    heaCheck1 = True
    heaCheck2 = True
    cooCheck1 = True
    cooCheck2 = True
    
    # GET TEST INFORMATION
    # --------------------

    print('\nTEST CASE INFORMATION\n---------------------')
    # Test case name
    name = requests.get('{0}/name'.format(url)).json()
    print('Name:\t\t\t\t{0}'.format(name))
    # Default simulation step
    step_def = requests.get('{0}/step'.format(url)).json()
    print('Default Simulation Step:\t{0}'.format(step_def))
    # --------------------

    # RUN TEST CASE
    # -------------
    # Reset test case

    print('Initializing the simulation.')
    res = requests.put('{0}/initialize'.format(url), data={'start_time': heatingScenario1[0], 'warmup_period': warmupPeriod})
    if res:
        print('Successfully initialized the simulation')
    # Set simulation step
    print('Setting simulation step to {0}.'.format(step))
    res = requests.put('{0}/step'.format(url), data={'step': step})
    
    print('\nRunning heating scenario 1...')
    # Initialize u
    u = initializeControls()
    print('\nRunning controller script...')
    # Simulation Loop

    print('\nSimulating heating period 1: February 5th to February 11th...')
    length = heatingScenario1[1] - heatingScenario1[0]
    for i in range(int(length / step)):
        y = requests.post('{0}/advance'.format(url), data=u).json()
        #print('Current simulated time: %d of %d' % (y['time'], heatingScenario1[1]), end = '\r')    
        print(y['time'], y['senTemRoom_y'], y['senHeaPow_y'], y['senFanPow_y'])    
        if y == None:
            print('\n ERROR: Simulation of heating period 1 failed')
            heaCheck1 = False
            break       
        
    if heaCheck1:
        print('\nCOMPLETED: Heating scenario 1')
        
    print('\nJumping to cooling period 1: May 7th to May 13th...')
    jump = coolingScenario1[0] - heatingScenario1[1]
    length = coolingScenario1[1] - coolingScenario1[0]
    res = requests.put('{0}/step'.format(url), data={'step': jump})
    y = requests.post('{0}/advance'.format(url), data=u).json()
    res = requests.put('{0}/step'.format(url), data={'step': step})
    print('\nSimulating cooling period 1: May 7th to May 13th...')
    for i in range(int(length / step)):
        y = requests.post('{0}/advance'.format(url), data=u).json()
        print('Current simulated time: %d of %d' % (y['time'], coolingScenario1[1]), end = '\r')        
        if y == None:
            print('\n ERROR: Simulation of cooling period 1 failed')
            cooCheck1 = False
            break       
        
    if cooCheck1:
        print('\nCOMPLETED: Cooling scenario 1')
        
        
    print('\nJumping to cooling period 2: July 23rd to July 29th...')
    jump = coolingScenario2[0] - coolingScenario1[1]
    length = coolingScenario2[1] - coolingScenario2[0]
    res = requests.put('{0}/step'.format(url), data={'step': jump})
    y = requests.post('{0}/advance'.format(url), data=u).json()
    res = requests.put('{0}/step'.format(url), data={'step': step})
    print('\nSimulating cooling period 2: July 23rd to July 29th...')
    for i in range(int(length / step)):
        y = requests.post('{0}/advance'.format(url), data=u).json()
        print('Current simulated time: %d of %d' % (y['time'], coolingScenario2[1]), end = '\r')         
        if y == None:
            print('\n ERROR: Simulation of cooling period 2 failed')
            cooCheck1 = False
            break       
        
    if cooCheck1:
        print('\nCOMPLETED: Cooling scenario 2')
        
    print('\nJumping to heating period 2: November 12th to November 18th...')
    
    jump = heatingScenario2[0] - coolingScenario2[1]
    length = heatingScenario2[1] - heatingScenario2[0]
    res = requests.put('{0}/step'.format(url), data={'step': jump})
    y = requests.post('{0}/advance'.format(url), data=u).json()
    res = requests.put('{0}/step'.format(url), data={'step': step})
    print('\nSimulating heating period 2: November 12th to November 18th...')
    for i in range(int(length / step)):
        y = requests.post('{0}/advance'.format(url), data=u).json()
        print('Current simulated time: %d of %d' % (y['time'], heatingScenario2[1]), end = '\r')         
        if y == None:
            print('\n ERROR: Simulation of heating period 2 failed')
            heaCheck2 = False
            break       
        
    if heaCheck2:
        print('\nCOMPLETED: Heating scenario 2')



    print('\nTesting complete.')
    
    

    return res

def initializeControls():
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

    u = {'PSZACcontroller_oveHeaPer1_u' : 0,
	'PSZACcontroller_oveHeaPer1_activate' : 0,
	'PSZACcontroller_oveHeaStpPer2_u' : 0,
	'PSZACcontroller_oveHeaStpPer2_activate' : 0,
	'PSZACcontroller_oveHeaStpPer3_u' : 0,
	'PSZACcontroller_oveHeaStpPer3_activate' : 0, 
	'PSZACcontroller_oveHeaStpPer1_u' : 0,
	'PSZACcontroller_oveHeaStpPer1_activate' : 0,
	'PSZACcontroller_oveHeaPer2_u' : 0,
	'PSZACcontroller_oveHeaPer2_activate' : 0,
	'PSZACcontroller_oveHeaStpPer4_u' : 0,
	'PSZACcontroller_oveHeaStpPer4_activate' : 0,
	'PSZACcontroller_oveCooCor_u' : 0,
	'PSZACcontroller_oveCooCor_activate' : 0,
	'PSZACcontroller_oveHeaCor_u' : 0,
	'PSZACcontroller_oveHeaCor_activate' : 0,
	'PSZACcontroller_oveDamP1_u' : 0,
	'PSZACcontroller_oveDamP1_activate' : 0,
	'PSZACcontroller_oveDamP3_u' : 0,
	'PSZACcontroller_oveDamP3_activate' : 0,
	'PSZACcontroller_oveDamP2_u' : 0,
	'PSZACcontroller_oveDamP2_activate' : 0,
	'PSZACcontroller_oveDamP4_u' : 0,
	'PSZACcontroller_oveDamP4_activate' : 0,
	'PSZACcontroller_oveCooStpPer4_u' : 0,
	'PSZACcontroller_oveCooStpPer4_activate' : 0,
	'PSZACcontroller_oveCooStpPer3_u' : 0,
	'PSZACcontroller_oveCooStpPer3_activate' : 0,
	'PSZACcontroller_oveCooStpPer2_u' : 0,
	'PSZACcontroller_oveCooStpPer2_activate' : 0,
	'PSZACcontroller_oveCooStpPer1_u' : 0,
	'PSZACcontroller_oveCooStpPer1_activate' : 0,
	'PSZACcontroller_oveCooStpCor_u' : 0,
	'PSZACcontroller_oveCooStpCor_activate' : 0,
	'PSZACcontroller_oveHeaStpCor_u' : 0,
	'PSZACcontroller_oveHeaStpCor_activate' : 0,
	'PSZACcontroller_oveDamCor_u' : 0,
	'PSZACcontroller_oveDamCor_activate' : 0,
	'PSZACcontroller_oveHeaPer4_u' : 0,
	'PSZACcontroller_oveHeaPer4_activate' : 0,
	'PSZACcontroller_oveCooPer4_u' : 0,
	'PSZACcontroller_oveCooPer4_activate' : 0,
	'PSZACcontroller_oveCooPer3_u' : 0,
	'PSZACcontroller_oveCooPer3_activate' : 0,
	'PSZACcontroller_oveCooPer2_u' : 0,
	'PSZACcontroller_oveCooPer2_activate' : 0,
	'PSZACcontroller_oveCooPer1_u' : 0,
	'PSZACcontroller_oveCooPer1_activate' : 0,
	'PSZACcontroller_oveHeaPer3_u' : 0,
	'PSZACcontroller_oveHeaPer3_activate' : 0,
         }

    return u

if __name__ == "__main__":
    res = run()
