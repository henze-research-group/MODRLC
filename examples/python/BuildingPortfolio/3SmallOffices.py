from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'actb_client'))
from actb_client import ActbClient, Portfolio

# Example of the dictionary that is expected by the Portfolio class.
# Testcase is the type of spawn model that will be run, e.g. 'spawnrefsmalloffice' or 'spawnrefmediumoffice'
# Initialization and Forecasting are identical to classic ACTB init and forecast arguments
# Step is... well... the simulation step.
# Finally, metamodel lets you switch between spawn (if metamodel = None) and a metamodel
# (if metamodel = 'name-of-the-test-case').

basicSOM = {'testcase' : 'spawnrefsmalloffice',
            'initialization' : {'start_time': 0, 'warmup_period': 0},
            'forecasting' : {'horizon' : 84600, 'interval' : 300},
            'step' : 300,
            'metamodel' : None
            } #todo add scenario

frenchSOM = {'testcase' : 'spawnrefsmalloffice-variant1',
            'initialization' : {'start_time': 0, 'warmup_period': 0},
            'forecasting' : {'horizon' : 84600, 'interval' : 300},
            'step' : 300,
            'metamodel' : None
            }

# We need to give a unique ID for each building using a dictionary as shown below.
# Here, we simply use 3 identical Small Office buildings for demonstration purposes, named 'first',
# 'second' and 'third'.

buildings = {'first' : basicSOM,
             'second' : frenchSOM,
             'third' : basicSOM
             }

# Initialize the building portfolio by passing the buildings dictionary

client = Portfolio(buildings=buildings)

# Initialize all the buildings at once

client.initialize_all()

# Define an empty control vector (i.e. give full control to the built-in rule-based controller)
u = {}

# Let us simulate 100 steps

for i in range(int(3600 * 24 * 7 / 300)):
    for id in buildings.keys():
        # We pass the id of the building we want to advance, and the control vector
        client.advance(id, u)
    print("Step {} of {}".format(i, int(3600 * 24 * 7 / 300)))

# Similarly to the advance method, we retrieve KPIs at the end of a simulation run.

for id in buildings.keys():
    print("KPIs for building named {}:".format(id))
    print(client.kpis(id))