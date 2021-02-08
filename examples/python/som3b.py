# -*- coding: utf-8 -*-
"""
This module is an example python-based testing interface.  It uses the
``requests`` package to make REST API calls to the test case container,
which mus already be running.  A controller is tested, which is
imported from a different module.

"""

# GENERAL PACKAGE IMPORT
# ----------------------
import requests
import numpy as np

# TEST CONTROLLER IMPORT
# ----------------------
from controllers.pidsom3b import compute_control, initialize

from simple_pid import PID
pid = PID(0.00005, 100, 300, setpoint=294.15, output_limits=(0,1), sample_time=0.01)

def run(plot=True, customized_kpi_config=None):
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
    #url = 'http://127.0.0.1:5000'
    url = 'http://0.0.0.0:5000'
    # Set simulation parameters
    length = 84600
    step = 60

    # ---------------

    actions = []

    # GET TEST INFORMATION
    # --------------------
    print('\nTEST CASE INFORMATION\n---------------------')
    # Test case name
    name = requests.get('{0}/name'.format(url)).json()
    print('Name:\t\t\t\t{0}'.format(name))
    # Inputs available
    inputs = requests.get('{0}/inputs'.format(url)).json()
    print('Control Inputs:\t\t\t{0}'.format(inputs))
    # Measurements available
    measurements = requests.get('{0}/measurements'.format(url)).json()
    print('Measurements:\t\t\t{0}'.format(measurements))
    # Default simulation step
    step_def = requests.get('{0}/step'.format(url)).json()
    print('Default Simulation Step:\t{0}'.format(step_def))
    # --------------------

    # Define customized KPI if any
    customizedkpis=[] # Initialize customzied kpi calculation list

    # --------------------

    # RUN TEST CASE
    # -------------
    # Reset test case
    print('Initializing the simulation.')
    res = requests.put('{0}/initialize'.format(url), data={'start_time':0,'warmup_period':0})
    if res:
        print('Successfully initialized the simulation')
    # Set simulation step
    print('Setting simulation step to {0}.'.format(step))
    res = requests.put('{0}/step'.format(url), data={'step':step})
    print('\nRunning test case...')
    # Initialize u
    u = initialize()
    print(u)
    # Simulation Loop
    for i in range(int(length/step)):
        # Advance simulation
        y = requests.post('{0}/advance'.format(url), data=u).json()
        print(y)
        # Compute next control signal
        u, action = compute_control(y, pid)
        actions.append(action)
        print(u)
        # Compute customized KPIs if any
    print('\nTest case complete.')
    # -------------

    # VIEW RESULTS
    # ------------
    # Report KPIs
    #kpi = requests.get('{0}/kpi'.format(url)).json()
    #print('\nKPI RESULTS \n-----------')
    #for key in kpi.keys():
    #    if key == 'tdis_tot':
    #        unit = 'Kh'
    #    if key == 'idis_tot':
    #        unit = 'ppmh'
    #    elif key == 'ener_tot':
    #        unit = 'kWh'
    #    elif key == 'cost_tot':
    #        unit = 'euro or $'
    #    elif key == 'emis_tot':
    #        unit = 'kg CO2'
    #    elif key == 'time_rat':
    #        unit = ''
    #    else:
    #        unit = 'No KPIs'
    #    print('{0}: {1} {2}'.format(key, kpi[key], unit))
    # ------------

    # POST PROCESS RESULTS
    # --------------------
    # Get result data
    res = requests.get('{0}/results'.format(url)).json()
    time = [x/3600 for x in res['y']['time']] # convert s --> hr
    TZone = [x-273.15 for x in res['y']['senTRoom_y']] # convert K --> C
    #TZone2 = [x-273.15 for x in res['y']['senTRoom2_y']] # convert K --> C
    #TZone3 = [x-273.15 for x in res['y']['senTRoom3_y']] # convert K --> C
    #TZone4 = [x-273.15 for x in res['y']['senTRoom4_y']] # convert K --> C
    #TZone5 = [x-273.15 for x in res['y']['senTRoom5_y']] # convert K --> C
    PHeat = res['y']['senHeaPow_y']
    #Pow = res['y']['senHPow_y']
    # Plot results
    if plot:
        from matplotlib import pyplot as plt
        plt.figure(1)
        plt.title('Core Zone Temperature')
        plt.plot(time, TZone)
        plt.plot(time, 20*np.ones(len(time)), '--')
        plt.plot(time, 23*np.ones(len(time)), '--')
        plt.ylabel('Temperature [C]')
        plt.xlabel('Time [hr]')
        plt.figure(2)
        plt.title('Heating Coil Power Demand')
        plt.plot(time, PHeat)
        plt.ylabel('Watts')
        plt.xlabel('Time [hr]')
        #plt.figure(3)
        #plt.title('Heating Coil control signal')
        #plt.plot(time, actions)
        #plt.ylabel('Control (unit)')
        #plt.xlabel('Time [hr]')
        #plt.figure(3)
        #plt.title('Perimeter Zone 1 Temperature')
        #plt.plot(time, TZone2)
        #plt.plot(time, 20*np.ones(len(time)), '--')
        #plt.plot(time, 23*np.ones(len(time)), '--')
        #plt.ylabel('Temperature [C]')
        #plt.xlabel('Time [hr]')
        #plt.figure(4)
        #plt.title('Perimeter Zone 2 Temperature')
        #plt.plot(time, TZone3)
        #plt.plot(time, 20*np.ones(len(time)), '--')
        #plt.plot(time, 23*np.ones(len(time)), '--')
        #plt.ylabel('Temperature [C]')
        #plt.xlabel('Time [hr]')
        #plt.figure(5)
        #plt.title('Perimeter Zone 3 Temperature')
        #plt.plot(time, TZone4)
        #plt.plot(time, 20*np.ones(len(time)), '--')
        #plt.plot(time, 23*np.ones(len(time)), '--')
        #plt.ylabel('Temperature [C]')
        #plt.xlabel('Time [hr]')
        #plt.figure(6)
        #plt.title('Perimeter Zone 4 Temperature')
        #plt.plot(time, TZone5)
        #plt.plot(time, 20*np.ones(len(time)), '--')
        #plt.plot(time, 23*np.ones(len(time)), '--')
        #plt.ylabel('Temperature [C]')
        #plt.xlabel('Time [hr]')
        plt.show()
    # --------------------

    return res

if __name__ == "__main__":
    res = run()
