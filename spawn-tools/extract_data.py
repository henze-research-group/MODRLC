import opyplus as op
import pandas as pd
from scipy import interpolate
import numpy as np
import os
import platform
import json
from ladybug.epw import EPW
from collections import OrderedDict


class FromEplus():

    def __init__(self,
                 resources_dir,
                 start_year="2017",
                 num_years = 3,
                 period=3600):
        '''Initialize the data index and data frame

        Parameters
        ----------
        resources_dir: string
            path to test case Resources directory
        start_time: string, default is "20170101 00:00:00"
            Pandas date-time indicating the starting
            time of the data frame.
        final_time: string, default is "20200101 00:00:00"
            Pandas date-time indicating the end time
            of the data frame.
        period: integer, default is 3600
            Number of seconds of the sampling time.

        '''
        self.start_year = start_year
        self.num_years = num_years
        self.resources_dir = resources_dir

        # search for weather file and IDF
        for file in os.listdir(self.resources_dir):
            if file.endswith('.epw'):
                self.weapath = os.path.join(self.resources_dir, file)
            if file.endswith('.idf'):
                self.idfpath = os.path.join(self.resources_dir, file)
        assert hasattr(self, 'weapath'), "Error: no EPW weather files found in {}".format(self.resources_dir)
        assert hasattr(self, 'idfpath'), "Error: no IDF files found in {}".format(self.resources_dir)

        # Create a date time index
        self.datetime_index = pd.date_range(
            start=pd.Timestamp(start_year + "0101 00:00:00"),
            end=pd.Timestamp(str(int(start_year) + num_years -1) + "1231 23:00:00"),
            freq='{period}s'.format(period=period))

        # Get an absolute time vector in seconds and save it
        time_since_epoch = self.datetime_index.asi8 / 1e9
        self.time = time_since_epoch - time_since_epoch[0]

        # save epmodel
        self.epm = op.Epm.load(self.idfpath)

    def generate_weather(self):

        #todo drop ladybug and use opyplus.WeatherData
        epwCls = EPW(self.weapath)

        epwDataList = epwCls.to_dict()['data_collections']
        epwDataDict = OrderedDict()

        for dataCol in epwDataList:
            dataName = dataCol['header']['data_type']['name']
            epwDataDict[dataName] = dataCol['values']
        yearlyWeather = pd.DataFrame(epwDataDict)
        weatherData = pd.concat([yearlyWeather]*self.num_years, ignore_index=True)
        weatherData.index = self.datetime_index
        weatherData['time'] = self.time
        drop = ['Year','Month','Day','Hour','Minute','Uncertainty Flags']
        weatherData.drop(columns=drop, axis=0)
        weatherData.to_csv(os.path.join(self.resources_dir, 'weather.csv'))

    def generate_emissions(self):

        # GWP100 (AR5) values from February 2016

        GWP = {'CH4' : 28,
               'N20' : 265
               }
        emissions = pd.DataFrame(index=self.datetime_index)
        emissions['time'] = self.time

        for fuel in self.epm.FuelFactors:
            if fuel.existing_fuel_resource_name == 'electricity':
                # In the IDF, values are in g/MJ. We convert to kg/kWh and apply the CO2-eq
                name = 'EmissionsElectricPower'
            elif fuel.existing_fuel_resource_name == 'naturalgas':
                name = 'EmissionsGasPower'
            else:
                name = None
            if name is not None:
                emissions[name] = [(fuel.co2_emission_factor / 3600
                                    + fuel.ch4_emission_factor * GWP['CH4'] / 3600
                                    + fuel.n2o_emission_factor * GWP['N20'] / 3600)
                                    * fuel.source_energy_factor        # apply the source conversion
                                    for i in range(len(emissions['time']))] # constant for now
        cols = emissions.columns
        assert ('EmissionsElectricPower' in cols and 'EmissionsGasPower' in cols), "Error: could not generate" \
                                                                                   "emissions.csv. Check that IDF contains" \
                                                                                   "fuel factors for electricity and natural" \
                                                                                   "gas."
        emissions.to_csv(os.path.join(self.resources_dir, 'emissions.csv'))

    def generate_prices(self):
        prices = pd.DataFrame(index=self.datetime_index)
        prices['month'] = self.datetime_index.month
        for tariff in self.epm.UtilityCost_Tariff:
            if tariff.demand_window_length is None:
                if tariff.output_meter_name == 'electricity:facility':
                    name = 'PriceElectricPower'
                elif tariff.output_meter_name == 'gas:facility':
                    name = 'PriceGasPower'

                charges = tariff.get_pointing_records()
                for charge in charges:
                    print(charge)
                    try:
                        print(charge.utility_cost_charge_block_name)
                    except:
                        pass
                    if hasattr(charge, 'utility_cost_charge_block_name') and name == 'PriceElectricPower':
                        # BOPTEST KPIs do not take energy blocks into account, so we average them here.
                        # we also prepare a tariff based on blocks for future usage.
                        # todo add dynamic and highly dynamic pricing
                        costBlocks = {}
                        for block in range(1, 16):
                            attr = getattr(charge, 'block_' + block + '_cost_per_unit_value_or_variable_name')
                            if attr is float:
                                costBlocks[getattr(charge, 'block_size_' + block + '_value_or_variable_name')] = attr
                        prices[name + 'Constant'] = np.mean([costBlocks[key] for key in costBlocks.keys()])
                    if hasattr(charge, 'january_value'):
                        monthlycosts = {'1' : charge.january_value,
                                        '2' : charge.february_value,
                                        '3' : charge.march_value,
                                        '4' : charge.april_value,
                                        '5' : charge.may_value,
                                        '6' : charge.june_value,
                                        '7' : charge.july_value,
                                        '8' : charge.august_value,
                                        '9' : charge.september_value,
                                        '10' : charge.october_value,
                                        '11' : charge.november_value,
                                        '12' : charge.december_value}
                        prices[name] = prices.apply(lambda row: monthlycosts[str(row)], axis=1)
        prices.to_csv(os.path.join(self.resources_dir, 'prices.csv'))