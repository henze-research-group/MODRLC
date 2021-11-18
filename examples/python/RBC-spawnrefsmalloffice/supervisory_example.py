import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'rulebased'))
from rbc import rulebased
import config


# Parameters

start_time = 0
warmup = 0
length = 24 * 3600 * 1
step = 300
control_level = 'supervisory'

# create RBC object
rbc = rulebased(config = config, step = step, level = control_level, start_time = start_time)

# initialize result to None
res = None

for i in range(int(length/step)):
    res = rbc.apply_control(res)

final_results = rbc.get_results()
final_kpis = rbc.get_kpis()
print(final_kpis)
