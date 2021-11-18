import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent / 'boptest_client'))
from boptest_client import BoptestClient


class rulebased():

    def __init__(self,
                 config,
                 kp_heating = 0.001,
                 kt_heating = 1/300,
                 curr_day = 0,
                 level = 'supervisory',
                 url = 'http://localhost:5000',
                 step = 300,
                 start_time = 0,
                 warmup = 0):

        self.client = BoptestClient(url = url)
        self.schedule = config.schedule
        self.controls = config.controls[level]
        self.level = level
        self.step = step
        try:
            self.dl = config.demandlimit
            self.dl_alarm = 0
            self.dl_alarm_time = 0
        except:
            self.dl = None

        self.zones = config.zones
        self.sensors = config.sensors
        self.kp_heating = kp_heating
        self.kt_heating = kt_heating
        self.start_time = start_time
        self.client.set_step(step = step)
        initparams = {'start_time' : start_time, 'warmup_period' : warmup}
        self.client.initialize(**initparams)

    def set_dl_alarm(self, result):
        dl_violation = False
        if result is not None:
            for zone in range(len(self.zones)):
                if result[self.sensors['ahuPower'][zone]] >= self.dl['maxpow'] and self.dl_alarm <= 3: #todo check max alarm level
                    self.dl_alarm +=1
                    dl_violation = True
                    break
            if (dl_violation == False):
                self.dl_alarm_time += self.step
                if self.dl_alarm_time >= 1800: #todo check how long it takes for an alarm to be cancelled
                    self.dl_alarm = 0 #todo check if levels go down one at a time or not
                    self.dl_alarm_time = 0

    def apply_control(self, result = None):

        if self.dl is not None:
            #todo include a function for setting a dl event depending on time
            self.set_dl_alarm(result)
        if self.level == 'supervisory':
            u = self.set_supervisory_controls(result)
        elif self.level == 'lowlevel':
            u = self.set_lowlevel_controls()
        return self.step_sim(u)

    def step_sim(self, u):
        return self.client.advance(control_u = u)

    def get_results(self):
        return self.client.results()

    def get_kpis(self):
        return self.client.kpis()

    def get_setpoint(self, time):
        print('Current simulation time: {}'.format(time))
        hour = (time / 3600) % 24
        day = int(hour / 24) % 7
        if day == 0:
            return min(self.schedule['tempSetpoints']['unoccupied']), \
                   max(self.schedule['tempSetpoints']['unoccupied'])
        elif day == 6:
            occ = self.schedule['occupied']['saturday']
        else:
            occ = self.schedule['occupied']['weekday']
        if min(occ) <= hour <= max(occ):
            return min(self.schedule['tempSetpoints']['occupied']), \
                   max(self.schedule['tempSetpoints']['occupied'])
        else:
            return min(self.schedule['tempSetpoints']['unoccupied']), \
                   max(self.schedule['tempSetpoints']['unoccupied'])

    def set_supervisory_controls(self, result):
        u = {}
        if result is not None:
            lostp, histp = self.get_setpoint(result['time'])
        else:
            lostp, histp = self.get_setpoint(self.start_time)
        for zone in range(len(self.zones)):
            u[self.controls['heating'][zone]] = lostp - self.dl_alarm
            u[self.controls['heating'][zone].replace('_u', '_activate')] = 1
            u[self.controls['cooling'][zone]] = histp + self.dl_alarm
            u[self.controls['cooling'][zone].replace('_u', '_activate')] = 1
        return u

def get_zone_temperatures(result):
    return [result[sensor] for sensor in self.sensors['zoneTemps']]


