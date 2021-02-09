# This file is a work in progress to run a particle swarm optimization of the SOM3 model.
#
# Tasks to be completed (probably in this order)
# 1. test submission of SOM3 model to alfalfa.
# 2. (optional) create a simpler test model that runs faster for testing
# 3. verify that an internal clock can run in alfalfa
# 4. create an f(x) method that batches a single simulation to alfalfa client
# 5. parse the results of alfalfa to return the cost function
# 6. initialize the PSO algorithms using the swarms package and assign f(x)
# 7. run the optimization and visualize the results
# 8. profit?

# Running the simulations requires setting up a few software stacks
#
# 1. start alfalfa with more than 1 worker (ideally n-2 where n is the number of cores/threads on machine)
# 2. `pip install examples/requirements.txt`
# 3. run this script by calling `python som3_mpc_pso.py`

from alfalfa_client.alfalfa_client import AlfalfaClient
from pathlib import Path

alfalfa_url = 'http://localhost'
client = AlfalfaClient(url=alfalfa_url)

model_path = Path(__file__).parent.absolute().parent.parent / 'testcases' / 'som3' / 'models' / 'wrapped.fmu'
print(model_path)
site = client.submit(model_path)

print('Starting simulation')
# eventually we will want to remove this external_clock. Not sure though since setting to timescale=5 does
# not work. And timescale has to be 1,2,...,15
length = 24 * 3600  # 48 hours
step = 300  # 5 minutes

# initial u
u = {'oveHCSet_u': 0,
     'oveHCSet_activate': 0,
     'oveVFRSet_u': 0,
     'oveVFRSet_activate': 0}

# Start and advance
client.start(site, external_clock=True)
for i in range(int(length / step)):
    client.setInputs(site, u)
    client.advance([site])
    model_outputs = client.outputs(site)
    print(model_outputs)

client.stop(site)
