import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent / 'actb_client'))
from actb_client import ActbClient


plot = [
    ['senTemRoom_y',
     'senTemRoom1_y',
     'senTemRoom2_y',
     'senTemRoom3_y',
     'senTemRoom4_y'
     ],
    ['senPowCor_y',
     'senPowPer1_y',
     'senPowPer2_y',
     'senPowPer3_y',
     'senPowPer4_y'
     ]
]
client = ActbClient(plot=plot, plothorizon=288)
# client = ActbClient(metamodel='spawnrefsmalloffice', plot=plot, plothorizon=288)
u = {"PSZACcontroller_oveHeaCor_u": 0,
     "PSZACcontroller_oveHeaPer1_u": 0,
     "PSZACcontroller_oveHeaPer2_u": 0,
     "PSZACcontroller_oveHeaPer3_u": 0,
     "PSZACcontroller_oveHeaPer4_u": 0}

#client = ActbClient()
client.stop_all()
initparams = {'start_time' : 24 * 3600, 'warmup_period' : 0}
client.initialize(**initparams, testcase='spawnrefsmalloffice-variant1')
client.set_step(step = 600)
print(client.inputs())
for i in range(2 * 288):
    client.advance(control_u=u)
