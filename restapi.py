# -*- coding: utf-8 -*-
"""
This module implements the REST API used to interact with the test case.
The API is implemented using the ``flask`` package.

"""

# GENERAL PACKAGE IMPORT
# ----------------------
from flask import Flask
from flask_restful import Resource, Api, reqparse
# ----------------------

# TEST CASE IMPORT
# ----------------
from testcase import TestCase
# ----------------

# FLASK REQUIREMENTS
# ------------------
app = Flask(__name__)
api = Api(app)
# ------------------

# INSTANTIATE TEST CASE
# ---------------------
case = TestCase()
# ---------------------

# DEFINE ARGUMENT PARSERS
# -----------------------
# ``step`` interface
parser_step = reqparse.RequestParser()
parser_step.add_argument('step')
# ``initialize`` interface
parser_initialize = reqparse.RequestParser()
parser_initialize.add_argument('start_time')
parser_initialize.add_argument('warmup_period')
# ``advance`` interface
parser_advance = reqparse.RequestParser()
for key in case.u.keys():
    parser_advance.add_argument(key)
#``forecast_parameters`` interface
parser_forecast_parameters = reqparse.RequestParser()
forecast_parameters = ['horizon','interval']
for arg in forecast_parameters:
    parser_forecast_parameters.add_argument(arg)
# ``price_scenario`` interface
parser_scenario = reqparse.RequestParser()
parser_scenario.add_argument('electricity_price')
# -----------------------

# DEFINE REST REQUESTS
# --------------------
class Advance(Resource):
    '''Interface to advance the test case simulation.'''

    def post(self):
        '''POST request with input data to advance the simulation one step
        and receive current measurements.'''
        u = parser_advance.parse_args()
        y = case.advance(u)
        return y

class Initialize(Resource):
    '''Interface to initialize the test case simulation.'''

    def put(self):
        '''PUT request to initialize the test.'''
        args = parser_initialize.parse_args()
        start_time = float(args['start_time'])
        warmup_period = float(args['warmup_period'])
        y = case.initialize(start_time,warmup_period)
        return y

class Step(Resource):
    '''Interface to test case simulation step size.'''

    def get(self):
        '''GET request to receive current simulation step in seconds.'''
        step = case.get_step()
        return step

    def put(self):
        '''PUT request to set simulation step in seconds.'''
        args = parser_step.parse_args()
        step = args['step']
        case.set_step(step)
        return step, 201

class Inputs(Resource):
    '''Interface to test case inputs.'''

    def get(self):
        '''GET request to receive list of available inputs.'''
        u_list = case.get_inputs()
        return u_list

class Measurements(Resource):
    '''Interface to test case measurements.'''

    def get(self):
        '''GET request to receive list of available measurements.'''
        y_list = case.get_measurements()
        return y_list

class Results(Resource):
    '''Interface to test case result data.'''

    def get(self):
        '''GET request to receive measurement data.'''
        Y = case.get_results()
        y_lists = {}
        u_lists = {}
        # np array to list
        for key in Y['y']:
            y_lists[key] = Y['y'][key].tolist()
        for key in Y['u']:
            u_lists[key] = Y['u'][key].tolist()
        Y_lists = {'y':y_lists, 'u':u_lists}
        return Y_lists

class KPI(Resource):
    '''Interface to test case KPIs.'''

    def get(self):
        '''GET request to receive KPI data.'''
        kpi = case.get_kpis()
        return kpi

class Forecast_Parameters(Resource):
    '''Interface to test case forecast parameters.'''

    def get(self):
        '''GET request to receive forecast parameters.'''
        forecast_parameters = case.get_forecast_parameters()
        return forecast_parameters

    def put(self):
        '''PUT request to set forecast horizon and interval inseconds.'''
        args = parser_forecast_parameters.parse_args()
        horizon  = args['horizon']
        interval = args['interval']
        case.set_forecast_parameters(horizon, interval)
        forecast_parameters = case.get_forecast_parameters()
        return forecast_parameters

class Forecast(Resource):
    '''Interface to test case forecast data.'''

    def get(self):
        '''GET request to receive forecast data.'''
        forecast = case.get_forecast()
        return forecast

class Scenario(Resource):
    '''Interface to test case scenario.'''

    def get(self):
        '''GET request to receive current scenario.'''
        scenario = case.get_scenario()
        return scenario

    def put(self):
        '''PUT request to set scenario.'''
        scenario = parser_scenario.parse_args()
        case.set_scenario(scenario)
        scenario = case.get_scenario()
        # It's needed to reset KPI Calculator when scenario is changed
        case.cal.initialize()
        return scenario

class Name(Resource):
    '''Interface to test case name.'''

    def get(self):
        '''GET request to receive test case name.'''
        name = case.get_name()
        return name
# --------------------

# ADD REQUESTS TO API WITH URL EXTENSION
# --------------------------------------
api.add_resource(Advance, '/advance')
api.add_resource(Initialize, '/initialize')
api.add_resource(Step, '/step')
api.add_resource(Inputs, '/inputs')
api.add_resource(Measurements, '/measurements')
api.add_resource(Results, '/results')
api.add_resource(KPI, '/kpi')
api.add_resource(Forecast_Parameters, '/forecast_parameters')
api.add_resource(Forecast, '/forecast')
api.add_resource(Scenario, '/scenario')
api.add_resource(Name, '/name')
# --------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0')
