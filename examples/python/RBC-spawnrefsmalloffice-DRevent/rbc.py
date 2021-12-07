import sys
from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'actb_client'))
from actb_client import ActbClient



class rulebased():

    def __init__(self,
                 config,
                 length,
                 kp_heating = 0.12,
                 ki_heating = 30,
                 curr_day = 0,
                 level = 'supervisory',
                 url = 'http://127.0.0.1:5000',
                 testcase='spawnrefsmalloffice',
                 step = 300,
                 start_time = 0,
                 warmup = 0):

        self.client = ActbClient(url = url)
        self.schedule = config.schedule
        self.controls = config.controls[level]
        self.hea_PI = [simple_PI(kp_heating, ki_heating, step) for control in self.controls['heating']]
        self.historian = {'temps' : [],
                          'power' : [],
                          'time' : [],
                          'lostp' : [],
                          'upstp' : []
                          }
        self.plotutils = {'lostp' : [min(self.get_setpoint('tempSetpoints', time)) - 273.15 for time in range(start_time, start_time + length + step, step)],
                          'histp' : [max(self.get_setpoint('tempSetpoints', time)) - 273.15 for time in range(start_time, start_time + length + step, step)],
                          'time' : [i / 3600 for i in range(0, length + step, step)]
                          }
        self.level = level
        self.step = step
        self.length = length
        try:
            self.dl = config.demandlimit
            self.dl_alarm = 0
            self.dl_alarm_time = 0
        except:
            self.dl = None

        self.zones = config.zones
        self.sensors = config.sensors
        self.start_time = start_time
        self.client.select(testcase)
        self.client.set_step(step = step)
        initparams = {'start_time' : start_time, 'warmup_period' : warmup}
        self.client.initialize(**initparams)
        self.fig, self.axes = plt.subplots(2, 1, figsize=(10,12))
        plt.ion()
        plt.show()


    def set_dl_alarm(self, result):
        dl_violation = False
        if result is not None:
            hod = (result['time'] / 3600) % 24
            is_dr_window = False
            for window in self.dl['time']:
                if window[0] <= hod <= window[1]:
                    is_dr_window = True
                    break
            for zone in range(len(self.zones)):
                if result[self.sensors['heatingPower'][zone]] >= self.dl['maxpow'] and is_dr_window: #todo check max alarm level
                    if zone == 1: #temporary fix
                        dl_violation = True
                        self.dl_alarm_time = 0
                        if self.dl_alarm <= 3:
                            self.dl_alarm +=1
                            break
            if (dl_violation == False):
                self.dl_alarm_time += self.step
                if self.dl_alarm_time >= 3600: #todo check how long it takes for an alarm to be cancelled
                    self.dl_alarm = 0 #todo check if levels go down one at a time or not
                    self.dl_alarm_time = 0

    def apply_control(self, result = None):
        if self.level == 'supervisory' and self.dl:
            u = self.set_supervisory_controls(result)
        elif self.level == 'lowlevel' and self.dl:
            u = self.set_lowlevel_controls(result)

        return self.step_sim(u)

    def step_sim(self, u):
        return self.client.advance(control_u = u)

    def get_results(self):
        return self.client.results()

    def get_kpis(self):
        return self.client.kpis()

    def get_setpoint(self, setpoint, time):
        hour = (time / 3600) % 24
        day = int(time / 3600 / 24) % 7
        if day == 0:
            return self.schedule[setpoint]['unoccupied']
        elif day == 6:
            occ = self.schedule['occupied']['saturday']
        else:
            occ = self.schedule['occupied']['weekday']
        if min(occ) <= hour <= max(occ):
            return self.schedule[setpoint]['occupied']
        else:
            return self.schedule[setpoint]['unoccupied']

    def set_supervisory_controls(self, result):
        u = {}
        if result is not None:
            stp = self.get_setpoint('tempSetpoints', result['time'])
            temps = [result[self.sensors['zoneTemps'][zone]] for zone in range(len(self.zones))]
            power = [result[self.sensors['heatingPower'][zone]] for zone in range(len(self.zones))]
            time = result['time']
        else:
            stp = self.get_setpoint('tempSetpoints', self.start_time)
            temps = [273.15 + 23 for zone in range(len(self.zones))]
            power = [0 for zone in range(len(self.zones))]
            time = self.start_time
        print('Current simulation time: {}'.format(time))
        lostp = min(stp)
        histp = max(stp)
        self.historian['temps'].append([temp - 273.15 for temp in temps])
        self.historian['power'].append(power)
        self.historian['time'].append(time)
        self.historian['lostp'].append(lostp - self.dl_alarm - 273.15)
        self.historian['upstp'].append(histp + self.dl_alarm - 273.15)
        self.set_dl_alarm(result)

        for zone in range(len(self.zones)):
            u[self.controls['heating'][zone]] = lostp - self.dl_alarm
            u[self.controls['heating'][zone].replace('_u', '_activate')] = 1
            u[self.controls['cooling'][zone]] = histp + self.dl_alarm
            u[self.controls['cooling'][zone].replace('_u', '_activate')] = 1
        return u

    def set_lowlevel_controls(self, result):
        u = {}
        if result is None:
            time = self.start_time
            cur_temp = [273.15 + 23 for zone in range(len(self.zones))]
            power = [0 for zone in range(len(self.zones))]
        else:
            time = result['time']
            cur_temp = [result[self.sensors['zoneTemps'][zone]] for zone in range(len(self.zones))]
            power = [result[self.sensors['heatingPower'][zone]] for zone in range(len(self.zones))]
        print('Current simulation time: {}'.format(time))

        # dampers
        dam_stp = self.get_setpoint('oasetpoints', time)
        temp_stp = self.get_setpoint('tempSetpoints', time)
        coo_stp = max(temp_stp)
        hea_stp = min(temp_stp)

        self.historian['temps'].append([temp - 273.15 for temp in cur_temp])
        self.historian['power'].append(power)
        self.historian['time'].append(time)

        for zone in range(len(self.zones)):
            zone_temp = cur_temp[zone]
            if zone_temp > coo_stp:
                coo_ove = 1
            else:
                coo_ove = 0
            u[self.controls['heating'][zone]] = self.hea_PI[zone].compute_u(zone_temp, hea_stp)
            u[self.controls['heating'][zone].replace('_u', '_activate')] = 1
            if u[self.controls['heating'][zone]] >= 0:
                u[self.controls['cooling'][zone]] = 0
            else:
                u[self.controls['cooling'][zone]] = coo_ove
            u[self.controls['cooling'][zone].replace('_u', '_activate')] = 1
            u[self.controls['damper'][zone]] = dam_stp[zone]
            u[self.controls['damper'][zone].replace('_u', '_activate')] = 1

        return u

    def plot(self, anim = 0, animate = False):
        temp = {}
        power = {}
        actualstplo = {}
        actualstpup = {}
        for zone, i in zip(self.zones, range(len(self.zones))):
            temp[zone] = [self.historian['temps'][j][i] for j in range(len(self.historian['temps']))]
            power[zone] = [self.historian['power'][j][i] for j in range(len(self.historian['power']))]

        time_hours = [(time - self.start_time) / 3600 for time in self.historian['time']]
        self.axes[0].cla()
        self.axes[1].cla()
        self.axes[0].set_title('Zone temperatures', fontweight='bold')
        self.axes[0].set_ylim(15, 27)
        self.axes[0].set_xlim(0, self.length / 3600)
        self.axes[0].set_xticks(range(0, int(self.length / 3600) + 6, 6))
        self.axes[0].set_ylabel('Temperature [C]')
        self.axes[0].set_yticks([i for i in range(15, 28)])
        self.axes[0].grid(which='both', linewidth=0.5, color='white')
        self.axes[0].set_facecolor("gainsboro")

        self.axes[1].set_title('Heating coil power demand (thermal)', fontweight='bold')
        self.axes[1].set_ylim(0 , 5000)
        self.axes[1].set_xlim(0, self.length / 3600)
        self.axes[1].set_xticks(range(0, int(self.length / 3600) + 6, 6))
        self.axes[1].set_ylabel('Watts [W]')
        self.axes[1].set_xlabel('Time [hours]')
        self.axes[1].set_yticks([i for i in range(0, 5500, 500)])
        self.axes[1].grid(which='both', linewidth=0.5, color='white')
        self.axes[1].set_facecolor("gainsboro")

        self.axes[0].plot(self.plotutils['time'], self.plotutils['lostp'], color='red', ls='--', label='Setpoints')
        self.axes[0].plot(self.plotutils['time'], self.plotutils['histp'], color='red', ls='--')
        for zone in self.zones:
            if zone == 'perimeter1': #temporary
                self.axes[0].plot(time_hours, temp[zone], label='Zone temperature')#label = zone)
                self.axes[1].plot(time_hours, power[zone], label='Power demand')#label = zone)
                self.axes[0].plot(time_hours, self.historian['lostp'], linestyle='--', color='black', label='Corrected setpoints')
                self.axes[0].plot(time_hours, self.historian['upstp'], linestyle='--', color='black')

        self.axes[0].axvspan(14, 18, alpha=0.5, color='red')
        self.axes[1].axvspan(14, 18, alpha=0.5, color='red')
        self.axes[1].axhline(y=500, xmin=0.583, xmax=0.75, color='black', linestyle='--', linewidth=2, label='Target demand limit')

        self.axes[1].legend(loc = 'upper right')
        self.axes[0].legend(loc = 'upper right')

        plt.tight_layout()
        plt.draw()
        plt.pause(0.5)
        if animate:
            plt.savefig("animation/anim_{}.png".format(str(anim)))
        plt.savefig('Results/RBC_{}.png'.format(self.level))

    def save_results(self):
        historian = pd.DataFrame(self.historian)
        historian.to_csv('Results/RBC_{}.csv'.format(self.level))
        kpis = self.get_kpis()
        with open('Results/kpis_{}.txt'.format(self.level), 'w') as file:
            file.write('Key performance indicators:\n')
            for key in kpis.keys():
                if key == 'tdis_tot':
                    file.write('Thermal discomfort: %.3f Kh\n'%(kpis[key]))
                if key == 'idis_tot':
                    file.write('Air quality discomfort: %.3f ppmh\n'%(kpis[key]))
                elif key == 'ener_tot':
                    file.write('Energy usage: %.3f kWh\n'%(kpis[key]))
                elif key == 'cost_tot':
                    file.write('Total cost: %.3f $\n'%(kpis[key]))
                elif key == 'emis_tot':
                    file.write('Total emissions: %.3f kg CO2\n'%(kpis[key]))


class simple_PI():

    def __init__(self, kp, ki, step):
        self.y = 0
        self.kp = kp
        self.ki = ki
        self.e = 0
        self.ei = 0
        self.step = step
        self.y_stp = 0

    def compute_u(self, y_meas, y_stp):
        self._e = self.e
        if y_stp != self.y_stp:
            self.ei = 0
            self.y_stp = y_stp
        self.e = y_stp - y_meas
        self.ei += self.e / self.step #(self.e - self._e)
        u = self.kp * self.e + self.ki * self.ei
        return min(max(u, 0), 1)


