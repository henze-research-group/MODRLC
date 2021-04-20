# -*- coding: utf-8 -*-
"""
This module creates an MPC controller for the SOM3 model.
"""
import json
import os
import sys
from pathlib import Path

# Allow access to boptest_client. boptest_client should be a separate package (like Alfalfa-client)
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent / 'boptest_client'))
from boptest_client import BoptestClient

# GENERAL PACKAGE IMPORT
# ----------------------
import numpy as np
import pandas as pd

# TEST CONTROLLER IMPORT
# ----------------------
from controllers.pidsom3b import initialize

# pid = PID(0.00005, 100, 300, setpoint=294.15)
from simple_pid import PID

pid = PID(Kp=5, Ki=240, Kd=0, setpoint=23 + 273.15, output_limits=(0, 1))


def control_u():
    u = {
        "oveHCSet_u": 1.0,
        "oveHCSet_activate": 1,
        "oveVFRSet_u": 0.7,
        "oveVFRSet_activate": 1,
        "oveCC_u": 0.0,
        "oveCC_activate": 1
    }
    return u


def run(plot=True, customized_kpi_config=None):
    """Run test case.

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

    """

    # create a path to store results
    save_dir = Path(__file__).absolute().with_suffix('')
    os.makedirs(save_dir, exist_ok=True)

    # Set simulation parameters
    # ---------------
    length = 8640
    step = 300

    actions = []

    # SETUP TEST CASE
    # ---------------
    url = 'http://localhost:5000'

    client = BoptestClient(url=url)
    print('\nTEST CASE INFORMATION\n---------------------')
    print(f'Name:\t\t\t\t{client.name()}')
    print(f'Control Inputs:\t\t\t{json.dumps(client.inputs(), indent=2)}')
    print(f'Measurements:\t\t\t{json.dumps(client.measurements(), indent=2)}')
    print(f'Default Simulation Step:\t\t\t{json.dumps(client.get_step(), indent=2)}')

    # Define customized KPI if any
    customizedkpis = []  # Initialize customized kpi calculation list

    # RUN TEST CASE
    # -------------
    # Reset test case
    print('Initializing the simulation')
    init_cond = client.initialize(start_time=0, warmup_period=0)
    print(f'Initial conditions: {init_cond}')
    print(f'Setting simulation step to {client.set_step(step=60)}')

    print('\nRunning test case...')
    # Initialize u in the pid controller
    u = initialize()

    # Simulation Loop
    for i in range(int(length / step)):
        y = client.advance()
        print(f"Step results")
        print(f"  TRoom: {y['senTRoom_y']}")

        # Compute next control signal
        # FOR MPC with perfect forecast, the compute control will optimize the forecast using PSO.
        # u, _action = compute_control(y, pid)
        u = control_u()
        print(json.dumps(u, indent=2))
        res = client.advance(control_u=u)
        print(f"New control signals")
        print(f"  oveHCSet_u: {u['oveHCSet_u']}")
        print(f"  oveVFRSet_u: {u['oveVFRSet_u']}")
        print(json.dumps(res, indent=2))

        # debug after 10
        # if i > 10:
        #     break

    print('\nTest case complete.')
    # -------------

    # VIEW RESULTS
    # ------------
    # Report KPIs
    kpis = client.kpis()
    print(f'KPIs:\n{json.dumps(kpis, indent=2)}')

    # POST PROCESS RESULTS
    # --------------------
    # Get result data
    results = client.results()
    print(results.keys())
    print(results['y'].keys())
    print(results['u'].keys())

    df = pd.DataFrame()
    for s in ['y', 'u']:
        for x in results[s].keys():
            if x != 'time':
                df = pd.concat((df, pd.DataFrame(data=results[s][x], index=results['y']['time'], columns=[x])), axis=1)
    df.index.name = 'time'
    df.to_csv(save_dir / 'results.csv')

    time = [x / 3600 for x in results['y']['time']]  # convert s --> hr
    TZone = [x - 273.15 for x in results['y']['senTRoom_y']]  # convert K --> C
    # TZone2 = [x-273.15 for x in results['y']['senTRoom2_y']] # convert K --> C
    # TZone3 = [x-273.15 for x in results['y']['senTRoom3_y']] # convert K --> C
    # TZone4 = [x-273.15 for x in results['y']['senTRoom4_y']] # convert K --> C
    # TZone5 = [x-273.15 for x in results['y']['senTRoom5_y']] # convert K --> C
    PHeat = results['y']['senHeaPow_y']
    # Pow = results['y']['senHPow_y']
    # Plot resultsults
    if plot:
        from matplotlib import pyplot as plt
        plt.figure(1)
        plt.title('Core Zone Temperature')
        plt.plot(time, TZone)
        plt.plot(time, 20 * np.ones(len(time)), '--')
        plt.plot(time, 23 * np.ones(len(time)), '--')
        plt.ylabel('Temperature [C]')
        plt.xlabel('Time [hr]')
        plt.figure(2)
        plt.title('Heating Coil Power Demand')
        plt.plot(time, PHeat)
        plt.ylabel('Watts')
        plt.xlabel('Time [hr]')
        # plt.figure(3)
        # plt.title('Heating Coil control signal')
        # plt.plot(time, actions)
        # plt.ylabel('Control (unit)')
        # plt.xlabel('Time [hr]')
        # plt.figure(3)
        # plt.title('Perimeter Zone 1 Temperature')
        # plt.plot(time, TZone2)
        # plt.plot(time, 20*np.ones(len(time)), '--')
        # plt.plot(time, 23*np.ones(len(time)), '--')
        # plt.ylabel('Temperature [C]')
        # plt.xlabel('Time [hr]')
        # plt.figure(4)
        # plt.title('Perimeter Zone 2 Temperature')
        # plt.plot(time, TZone3)
        # plt.plot(time, 20*np.ones(len(time)), '--')
        # plt.plot(time, 23*np.ones(len(time)), '--')
        # plt.ylabel('Temperature [C]')
        # plt.xlabel('Time [hr]')
        # plt.figure(5)
        # plt.title('Perimeter Zone 3 Temperature')
        # plt.plot(time, TZone4)
        # plt.plot(time, 20*np.ones(len(time)), '--')
        # plt.plot(time, 23*np.ones(len(time)), '--')
        # plt.ylabel('Temperature [C]')
        # plt.xlabel('Time [hr]')
        # plt.figure(6)
        # plt.title('Perimeter Zone 4 Temperature')
        # plt.plot(time, TZone5)
        # plt.plot(time, 20*np.ones(len(time)), '--')
        # plt.plot(time, 23*np.ones(len(time)), '--')
        # plt.ylabel('Temperature [C]')
        # plt.xlabel('Time [hr]')
        plt.show()


if __name__ == "__main__":
    run()
