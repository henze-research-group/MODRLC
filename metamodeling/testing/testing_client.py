import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent / 'actb_client'))
from actb_client import ActbClient
from matplotlib import pyplot as plt

client = ActbClient(url='http://127.0.0.1:80', metamodel='spawnrefsmalloffice')
client.stop_all()
client.init_metamodel(additionalstates=None, start_time=0, forecast_horizon=84600)
y = []
for i in range(100):
    fcast = client.get_metamodel_forecast()
    print(fcast)
    y.append(client.step_metamodel({'PSZACcontroller_oveHeaPer1_u' : 1}))

plt.figure()
plt.plot(y)
plt.show()
