# Python client for communicating with the ACTB.

import json
import os
from pathlib import Path
import requests
import numpy as np
import pandas as pd


class ActbClient:

    def __init__(self, url='http://127.0.0.1:80', metamodel=None):
        self.url = url
        self.metamodel = metamodel
        self.jsonpath = str(Path(__file__).parent.absolute() / 'jobs.json')
        #todo: add a metamodel client

    def init_metamodel(self, additionalstates=None, start_time=0, forecast_horizon=84600):
        # define resources and metamodel path

        # todo: include actual y values to initialize at different start times. Use the actual y value and Kalman gain to set the correct x state

        resourcesdir = str(Path(__file__).parent.absolute().parent / 'testcases' / 'SpawnResources' / self.metamodel)
        metamodeldir = str(Path(__file__).parent.absolute().parent / 'testcases' / 'SpawnResources' / self.metamodel / 'metamodel')

        # load metamodel matrices and resources
        self.Amat = np.load(os.path.join(metamodeldir, 'A.npy'))
        self.Bmat = np.load(os.path.join(metamodeldir, 'B.npy'))
        self.Cmat = np.load(os.path.join(metamodeldir, 'C.npy'))
        self.Dmat = np.zeros(self.Cmat.shape)
        self.x0 = np.load(os.path.join(metamodeldir, 'x0.npy'))
        datafrommodel = pd.read_csv(os.path.join(resourcesdir, 'dataFromModel.csv'), index_col=False)
        weather = pd.read_csv(os.path.join(resourcesdir, 'weather.csv'), index_col=False)
        emissions = pd.read_csv(os.path.join(resourcesdir, 'emissions.csv'), index_col=False)
        prices = pd.read_csv(os.path.join(resourcesdir, 'prices.csv'), index_col=False)

        spawndataset = pd.read_csv(os.path.join(metamodeldir, 'spawnDataset.csv'), index_col=False)
        self.tvps = pd.concat([datafrommodel, weather, emissions, prices, spawndataset], axis=1)
        lengths = [len(a) for a in [datafrommodel, weather, emissions, prices, spawndataset]]
        self.tvps = self.tvps.iloc[min(lengths):]
        # load metamodel config
        with open(os.path.join(metamodeldir, 'config.json'), 'r') as configfile:
            self.mconfig = json.load(configfile)
        tvps = self.mconfig['tvps']
        self.outputs = self.mconfig['outputs']

        if additionalstates is not None:
            tvps.extend(additionalstates)
        self.tvps = self.tvps[tvps]
        self.start_time = start_time
        self.time = self.start_time
        self.horizon = forecast_horizon

    def extract_uvect(self, control):
        u = []
        index = int((self.time - self.start_time)/self.mconfig['step'])
        for element in self.mconfig['uvect']:
            if element in self.tvps.columns:
                u.extend([self.tvps[element].iloc[index].values[0]])
            elif element in control.keys():
                u.extend([control[element]])
            else:
                raise AttributeError("Could not find variable {} in tvps or control vector".format(element))
        return np.array(u)

    def get_metamodel_forecast(self):
        cur_ind = int((self.time - self.start_time)/self.mconfig['step'])
        hor_ind = int((self.time + self.horizon - self.start_time)/self.mconfig['step'])
        return self.tvps.iloc[cur_ind:hor_ind]

    def step_metamodel(self, control):

        u = self.extract_uvect(control)
        y = self.Cmat @ self.x0
        self.x0 = self.Amat @ self.x0 + self.Bmat @ u
        yout = {}
        for i, key in zip(range(len(y)), self.outputs):
            yout[key] = y[i]
        self.time+=self.mconfig['step']

        return y

    def name(self):
        """Return the name of the testcase that is loaded in the ACTB.

        Note that this method only returns a single value and not a
        dictionary. For example, it returns b'60.0\n', which is not JSON, but when calling json() it returns
        the value. It is recommended to update the /name method in BOPTEST to return JSON (e.g., {"name": "tc1"}

        Returns
            String
        """
        return requests.get('{0}/name/{1}'.format(self.url, self.simId)).json()

    def inputs(self):
        """Return the list of inputs for the ACTB testcase that has been loaded

        Returns:
            Dict of inputs
        """
        return requests.get('{0}/inputs/{1}'.format(self.url, self.simId)).json()

    def measurements(self):
        """Return a list of measurements available in the loaded ACTB testcase

        Returns:
            Dict of measurements
        """
        return requests.get('{0}/measurements/{1}'.format(self.url, self.simId)).json()

    def get_step(self, test_id=None):
        """Return the timestep configuration.

        Note that this method only returns a single value and not a
        dictionary. For example, it returns b'60.0\n', which is not JSON, but when calling json() it returns
        the value. It is recommended to update the /step method in BOPTEST to return JSON (e.g., {"step": 60}


        Returns:
            String
        """

        return requests.get('{0}/step/{1}'.format(self.url, self.simId)).json()

    def set_step(self, step=60):
        """Set the step duration the simulation through time at step level defined

        Note that this method only returns a single value and not a
        dictionary. For example, it returns b'60.0\n', which is not JSON, but when calling json() it returns
        the value. It is recommended to update the /step method in BOPTEST to return JSON (e.g., {"step": 60}

        Returns:
            step size (str): the value of the step that was set
        """
        self.step = step
        requests.put('{0}/step/{1}'.format(self.url, self.simId), data={'step' : step})

    def reset(self, **kwargs):
        self.stop()
        self.select(self.testcase)
        self.set_step(step = self.step)
        return self.initialize(self.testcase, **kwargs)

    def initialize(self,testcase, **kwargs):
        """Initialize a testcase

        Parameters:
            test_id (str): if provided, then the test_id to initialize. If None, then it will assume that a testcase
                           was initialized.
            **kwargs: other options to pass as the data. Valid options are start_time, warmup_period

        Returns:
            initial values (dict): the initialized conditions.

        """

        self.stop_all()
        self.select(testcase)
        # merge the default args with the kwargs
        default = {'start_time': 0, 'warmup_period': 0}
        data = {**default, **kwargs}
        res = requests.put('{0}/initialize/{1}'.format(self.url, self.simId), data=data)
        print(res)
        if res:
            return res.json()
        else:
            result = {"status": "error", "message": "unable to submit simulation"}
            raise Exception(result)

    def advance(self, control_u={}):
        """Advance the simulation through time at step level defined

        Parameters:
            control_u (dict): control values to set

        Returns:
            simulation results (dict): values of the model at the the last step
        """
        return requests.post('{0}/advance/{1}'.format(self.url, self.simId), data=control_u).json()

    def kpis(self):
        """Return the KPIs of the testcase.

        Returns:
            kpis (dict): results of the kpis
        """
        return requests.get('{0}/kpi/{1}'.format(self.url, self.simId)).json()

    def results(self):
        """Return the results of the simulation.

        """
        return requests.get('{0}/results/{1}'.format(self.url, self.simId)).json()

    def get_testcases(self):
        """Lists available testcases
        """
        return requests.get('{0}/testcases'.format(self.url))

    def select(self, testcase):
        """Selects a testcase
        """
        self.testcase = testcase
        self.simId = requests.post('{0}/testcases/{1}/select'.format(self.url, testcase)).json()['testid']
        if os.path.isfile(self.jsonpath):
            with open(self.jsonpath, 'r') as data_file:
                data = json.load(data_file)
        else:
            data = {testcase: []}
        if testcase not in data.keys():
            data[testcase] = []
        data[testcase].append({'simId' : self.simId,
                               'url' : self.url,
                               'placeholder' : None})
        print(data)
        with open(self.jsonpath, 'w') as data_file:
            json.dump(data, data_file)


    def inputs(self):
        """Get available testcase inputs
        Returns:
            A list of available inputs
        """
        return requests.get('{0}/inputs/{1}'.format(self.url, self.simId)).json()

    def get_forecasts(self):
        """Request a forecast
        Returns:
            Forecast at the current timestep, using the default or customized horizon and interval
        """
        return requests.get('{0}/forecast/{1}'.format(self.url, self.simId)).json()

    def get_forecast_parameters(self):
        """Get the current forecast parameters
        Returns:
            Current forecast horizon and interval
        """
        return requests.get('{0}/forecast_parameters/{1}'.format(self.url, self.simId)).json()

    def set_forecast_parameters(self, horizon, interval):
        """Set new forecast parameters
        Parameters:
            horizon: forecast horizon in seconds
            interval: interval between forecasts in seconds

        """
        data = {'horizon' : horizon, 'interval' : interval}
        requests.put('{0}/forecast_parameters/{1}'.format(self.url, self.simId), data=data)

    def get_scenario(self):
        return requests.get('{0}/scenario/{1}'.format(self.url, self.simId)).json()

    def set_scenario(self, elec_pricing):
        data = {'electricity_price' : elec_pricing}
        requests.put('{0}/scenario/{1}'.format(self.url, self.simId), data=data).json()

    def stop(self):
        requests.put('{0}/stop/{1}'.format(self.url, self.simId))
        if os.path.isfile(self.jsonpath):
            with open(self.jsonpath, 'r') as data_file:
                data = json.load(data_file)
        else:
            raise UserWarning("No jobs.json file: cannot update test case list.")
        for key, job in enumerate(data[self.testcase]):
            if job['simId'] == self.simId:
                data[self.testcase].pop(key)
        with open(self.jsonpath, 'w') as data_file:
            data = json.dump(data, data_file)

    def stop_all(self):
        if os.path.isfile(self.jsonpath):
            with open(self.jsonpath, 'r') as data_file:
                data = json.load(data_file)
        else:
            print("No jobs.json file: cannot stop all test cases.")
            return
        for testcase in data.keys():
            for key, job in enumerate(data[testcase]):
                requests.put('{0}/stop/{1}'.format(job['url'], job['simId']))
                print("Stopped instance {} of test case {}".format(job['simId'], testcase))
                data[testcase].pop(key)
        with open(self.jsonpath, 'w') as data_file:
            data = json.dump(data, data_file)
