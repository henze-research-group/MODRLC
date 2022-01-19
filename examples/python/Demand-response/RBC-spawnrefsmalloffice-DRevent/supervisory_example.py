from rbc import rulebased
import config


# Parameters

start_time = 3 * 24 * 3600
warmup = 0
length = 24 * 3600 * 1
step = 300
control_level = 'supervisory'
plot = True
# create RBC object
rbc = rulebased(url = 'http://localhost:80', config =config, step = step, level = control_level, start_time = start_time, length = length)
# initialize result to None
res = None

for i in range(int(length/step)):
    res = rbc.apply_control(res)
    if plot:
        rbc.plot(animate=True, anim=i)

final_results = rbc.get_results()
final_kpis = rbc.get_kpis()
rbc.save_results()
input("Simulation ended successfully!\nResults have been saved in the Results/ folder.\nPress enter to exit.")
