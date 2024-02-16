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
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'actb_client'))
from actb_client import ActbClient

# ----------------------

def rePlot(axs, lostp, upstp, kpis, xs, ys):

    # Draw x and y lists
    axs[0].cla()
    axs[1].cla()
    axs[2].cla()
    axs[3].cla()
    axs[4].cla()
    axs[0].set_title('Perimeter Zone 1 temperature')
    axs[0].set_ylim(273.15 + 15, 273.15 + 27)
    axs[0].set_ylabel('Temperature (°C)')
    axs[0].set_xlabel('Time (seconds)')

    axs[0].plot(xs, lostp, color='red')
    axs[0].plot(xs, upstp, color='red')
    axs[0].plot(xs, ys, color='blue')

    axs[1].set_title('Tdis (Kh)')
    axs[1].bar(1, kpis['tdis_tot'])

    axs[2].set_title('Energy (kWh)')
    axs[2].bar(1, kpis['ener_tot'])

    axs[3].set_title('Cost ($)')
    axs[3].bar(1, kpis['cost_tot'])

    axs[4].set_title('Emissions (kgCO2)')
    axs[4].bar(1, kpis['emis_tot'])

    plt.draw()
    plt.pause(0.5)

    return None

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
    url = 'http://localhost:80'
    # Set simulation parameters
    length = 84600
    start = 3*length
    step = 600
    testcase = 'spawnrefsmalloffice'

    client = ActbClient(url=url)

    # Define customized KPI if any
    customizedkpis=[] # Initialize customzied kpi calculation list

    # --------------------

    # RUN TEST CASE
    # -------------
    # Reset test case
    print('Initializing the simulation.')
    initparams = {'start_time':start,'warmup_period':0}
    res = client.initialize(testcase, **initparams)

    if res:
        print('Successfully initialized the simulation')
    # Set simulation step
    print('Setting simulation step to {0}.'.format(step))
    client.set_step(step = step)
    # Set the forecast for plotting utility
    client.set_forecast_parameters(length, step)

    forecast_point_names = ['LowerSetp[perimeter_zn_1]', 'UpperSetp[perimeter_zn_1]']
    forecast = client.get_forecasts(
        horizon = length,
        interval = step,
        point_names = forecast_point_names
    )

    print('\nRunning test case...')
    # Initialize u
    u = {}
    # Initialize plot
    fig, axs = plt.subplots(1, 5, gridspec_kw = {'width_ratios': [5, 1, 1, 1, 1]})
    xs = []
    tP1 = []
    lostp = []
    upstp = []
    hourstoplot = 24
    plt.ion()
    plt.show()

    # Simulation Loop
    for i in range(int(length/step)):
        # Advance simulation
        y = client.advance(control_u = u)
        kpis = client.kpis()
        xs.append(y['time']-start)
        tP1.append(y['senTemRoom1_y'])
        lostp.append(forecast['LowerSetp[perimeter_zn_1]'][i])
        upstp.append(forecast['UpperSetp[perimeter_zn_1]'][i])
        lostp = lostp[-(int(hourstoplot*3600/step)):]
        upstp = upstp[-(int(hourstoplot*3600/step)):]
        xs = xs[-(int(hourstoplot*3600/step)):]
        tP1 = tP1[-(int(hourstoplot * 3600 / step)):]
        rePlot(axs, lostp, upstp, kpis, xs, tP1)

    print('\nTest case complete.')
    # -------------

    # VIEW RESULTS
    # ------------
    # Report KPIs
    kpi = client.kpis()
    print('\nKPI RESULTS \n-----------')
    for key in kpi.keys():
        if key == 'tdis_tot':
            unit = 'Kh'
        if key == 'idis_tot':
            unit = 'ppmh'
        elif key == 'ener_tot':
            unit = 'kWh'
        elif key == 'cost_tot':
            unit = 'euro or $'
        elif key == 'emis_tot':
            unit = 'kg CO2'
        elif key == 'time_rat':
            unit = ''
        print('{0}: {1} {2}'.format(key, kpi[key], unit))
    # ------------

    # POST PROCESS RESULTS
    # --------------------
    # Get result data
    res = client.results()
    # --------------------

    return res

if __name__ == "__main__":
    res = run()
