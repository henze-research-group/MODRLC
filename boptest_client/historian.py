# Library for storing results of BOPTEST-service's API to a historian/csv/dataframe.

# Author: Nicholas Long <https://github.com/nllong>

import os

import pandas as pd


class Conversions:
    @classmethod
    def deg_k_to_c(cls, kelvin):
        return kelvin - 273.15


class Historian(object):
    def __init__(self, time_step=1):
        """
        :param time_step: int, time step in minutes
        """
        self.data = {}
        self.name_map = {}
        self.units = {}
        self.conversion_map = {}
        self.time_step = time_step

    def add_point(self, name, units, point_name, f_conversion=None):
        """
        Add a point to store to the historian
        :param name: string, name of the datapoint. Must be convertible into dict key and dataframe column
        :param units: string, units in which the values are stored
        :param point_name: string, name of the point to extract from the model output dictionary from Alfalfa
        :param f_conversion: function pointer, function to call to convert the value
        :return:
        """
        if name in self.data.keys():
            raise Exception(f'Historian point already exists for {name}')

        self.data[name] = []
        self.conversion_map[name] = f_conversion
        self.units[name] = units

        if point_name is not None:
            if point_name in self.name_map.keys():
                raise Exception(f'Point name in name map already exists for {point_name}')

            self.name_map[point_name] = name

    def add_data(self, values):
        """
        Append the data in the fields into the mapped column names. Pulls data out of values and
        into the historian.
        :param values: dict
        """

        for point_name, value in values.items():
            if point_name in self.name_map:
                name = self.name_map[point_name]
                # print(f"name {name} and point {point_name} with value {value}")
                f = self.conversion_map[name] if self.conversion_map[name] is not None else None
                if f:
                    value = f(value)
                self.data[name].append(value)
            else:
                # point_name is not registered in historian, skipping
                pass

    def add_datum(self, name, value):
        f = self.conversion_map[name] if self.conversion_map[name] is not None else None

        if f:
            value = f(value)
        self.data[name].append(value)

    def rm_incorrect_length_vals_from_data(self):
        num_timesteps = len(self.data['timestamp'])
        to_rm = []
        for point, data in self.data.items():
            if len(data) != num_timesteps:
                to_rm.append(point)
        for p in to_rm:
            self.data.pop(p)

    def to_df(self):
        # create the time index
        f = '{}T'.format(self.time_step)
        ind = pd.date_range(
            start=self.data['timestamp'][0], end=self.data['timestamp'][-1], freq=f
        )
        return pd.DataFrame(self.data, index=ind)

    def save_csv(self, filepath, filename):
        os.makedirs(filepath, exist_ok=True)

        self.to_df().to_csv(f'{filepath}/{filename}')

    def save_pickle(self, filepath, filename):
        os.makedirs(filepath, exist_ok=True)

        self.to_df().to_pickle(f'{filepath}/{filename}')

    def evaluate_performance(self):
        """
        Return the overall performance of the control
        Assumptions:
            * Timestep is 5 Minutes
            * Occupied hours are between 0800 and 1800
            * Variables are named: timestamp, PPD, TotalHVACPower
        :return: dict of performance indicators
        """
        df = self.to_df()
        df_occ_hours = df.between_time('08:00', '18:00')

        total_hours = len(df.index) / 12
        total_hours_occupied = len(df_occ_hours.index) / 12
        total_hvac_energy = df.sum(axis=0)['TotalHVACPower'] / 12 / 1000  # kwh
        total_hvac_energy_occupied = df_occ_hours.sum(axis=0)['TotalHVACPower'] / 12 / 1000  # kwh
        average_ppd = df.mean(axis=0)['PPD']
        average_ppd_occupied = df_occ_hours.mean(axis=0)['PPD']
        # average_ppd_occupied = df_occ_hours.mean(axis=0)['PPD']  # this is not valuable

        return {
            'start_time': df['timestamp'].iloc[0].strftime('%m/%d/%Y %H:%M:%S'),
            'end_time': df['timestamp'].iloc[-1].strftime('%m/%d/%Y %H:%M:%S'),
            'total_hours': total_hours,
            'total_hours_occupied': total_hours_occupied,
            'total_hvac_energy': total_hvac_energy,
            'total_hvac_energy_occupied': total_hvac_energy_occupied,
            'average_ppd': average_ppd,
            'average_ppd_occupied': average_ppd_occupied,
        }
