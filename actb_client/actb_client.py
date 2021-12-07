# Python client for communicating with the ACTB.

import json
import os
import time
import uuid
from collections import OrderedDict

import requests
from requests_toolbelt import MultipartEncoder


class ActbClient:

    def __init__(self, url='http://127.0.0.1:5000', metamodel=None):
        self.url = url
        self.metamodel = metamodel
        #todo: add a metamodel client

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

        requests.put('{0}/step/{1}'.format(self.url, self.simId), data={'step' : step})

    def initialize(self, **kwargs):
        """Initialize a testcase

        Parameters:
            test_id (str): if provided, then the test_id to initialize. If None, then it will assume that a testcase
                           was initialized.
            **kwargs: other options to pass as the data. Valid options are start_time, warmup_period

        Returns:
            initial values (dict): the initialized conditions.

        """
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
        return requests.get('{0}/results/{1}'.format(self.url, self.simId))

    def get_testcases(self):
        """Lists available testcases
        """
        return requests.get('{0}/testcases'.format(self.url))

    def select(self, testcase):
        """Selects a testcase
        """
        self.simId = requests.post('{0}/testcases/{1}/select'.format(self.url, testcase)).json()['testid']

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