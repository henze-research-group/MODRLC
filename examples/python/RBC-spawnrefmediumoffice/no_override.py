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
url = 'http://localhost:80'
# Set simulation parameters
length = 84600
start = 0
step = 600
testcase = 'spawnrefmediumoffice'

client = ActbClient(url=url)

# --------------------

# RUN TEST CASE
# -------------
# Reset test case
print('Initializing the simulation.')
initparams = {'start_time':start,'warmup_period':0}
res = client.initialize(testcase, **initparams)
if res:
    print('Successfully initialized the simulation')
else:
    print('Something failed')
# Set simulation step
print('Setting simulation step to {0}.'.format(step))
client.set_step(step = step)
# Set the forecast for plotting utility
client.set_forecast_parameters(length, step)
#forecast = client.get_forecasts()


print('\nRunning test case...')
# Initialize u
u = {}
# Initialize plot

# Simulation Loop
for i in range(int(length/step)):
    # Advance simulation
    y = client.advance(control_u = u)
    kpis = client.kpis()
    print('Progress: %.2f %' % (i/int(length/step)))


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