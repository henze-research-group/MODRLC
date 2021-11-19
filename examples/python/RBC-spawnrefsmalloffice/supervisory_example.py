from rbc import rulebased
import config


# Parameters

start_time = 3 * 24 * 3600 + 5 * 3600
warmup = 0
length = 24 * 3600 * 1
step = 300
control_level = 'supervisory'
plot = True
# create RBC object
rbc = rulebased(config = config, step = step, level = control_level, start_time = start_time, length = length)

# initialize result to None
res = None

for i in range(int(length/step)):
    res = rbc.apply_control(res)
    if plot:
        rbc.plot()

final_results = rbc.get_results()
final_kpis = rbc.get_kpis()
print(final_kpis)
