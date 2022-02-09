from pathlib import Path

import numpy as np
import pandas as pd
import datetime


class ModelParameters:
    """This class will be instantiated in various models, so make sure that there are no
    data intensive operations in it."""

    def __init__(self):

        # Load in the N4SID matrices
        p = Path('').resolve().parent.parent.parent / 'testcases' / 'SpawnResources' / 'spawnrefsmalloffice' / 'metamodel'
        if p.exists():
            # States are room temperatures, <to flesh out>
            self.a = np.load(p / 'A.npy')
            self.b = np.load(p / 'B.npy')
            self.c = np.load(p / 'C.npy')
            # D array is zeroed out for the length of the inputs in _u
            self.d = np.array([[0, 0, 0, 0]])
            self.K = np.load(p / 'K.npy')
            # use the last column of the data per Thibault's comment
            self.x0 = np.transpose([np.load(p / 'x0.npy')])
            print("Finished loading matrices")

            weatherpath = p.resolve().parent / 'weather.csv'
            pricespath = p.resolve().parent / 'prices.csv'
            modeldatapath = p.resolve().parent / 'dataFromModel.csv'

            if not weatherpath.exists():
                raise Exception("There is no weather file. Make sure you generated it.")
            elif not pricespath.exists():
                raise Exception("There is no energy prices file. Make sure you generated it.")
            elif not modeldatapath.exists():
                raise Exception("There is no model data file. Make sure you generated it.")
            # if not tvp_file.exists():
            #     raise Exception("There is no time varying parameter file, make sure to unzip wrapped 2.7z")

            self.modeldata = pd.read_csv(modeldatapath)
            self.weather = pd.read_csv(weatherpath)
            self.prices = pd.read_csv(pricespath)

            epoch = 1577836800 #starting in 2020
            self.modeldata['time'] = self.modeldata['time'].apply(toEpoch, args=[epoch])
            self.modeldata.set_index(pd.to_datetime(self.modeldata['time'], unit='s'), inplace=True)
            self.weather['time'] = self.weather['time'].apply(toEpoch, args=[epoch])
            self.weather.set_index(pd.to_datetime(self.weather['time'], unit='s'), inplace=True)
            self.prices['time'] = self.prices['time'].apply(toEpoch, args=[epoch])
            self.prices.set_index(pd.to_datetime(self.prices['time'], unit='s'), inplace=True)



        else:
            raise Exception(f"metamodeling path does not exist at {p}")

        # Additional states
        #   todo: remember which state is which. The first is the predicted temp.
        self.additional_x_states_inits = np.array([[293], [0], [0], [0], [0]])

        # The min_x is +/- 10 for the number of rows of A which is the # of states
        self.min_x = np.array([[-30]] * self.a.shape[0])
        self.max_x = - self.min_x

        # Indoor temperature bounds
        self.min_indoor_t = np.array([250])
        self.max_indoor_t = np.array([310])

        self.min_setpoint_t = np.array([293])
        self.max_setpoint_t = np.array([298])

        self.min_cooling = 0
        self.max_cooling = 1
        self.min_heating = 0
        self.max_heating = 1

        # These are the variables that are needed to define the u matrix.
        self.variables = []

        # Weather data

        self.variables.append({
            "type": "tvp",
            "data_source": "weather",
            "var_name": "TDryBul",
            "data_column_name": "TDryBul",
            "local_var_name": "t_dry_bulb",
        })

        self.variables.append({
            "type": "tvp",
            "data_source": "weather",
            "var_name": "HGloHor",
            "data_column_name": "HGloHor",
            "local_var_name": "h_glo_hor",
        })

        self.variables.append({
            "type": "tvp",
            "data_source": "modeldata",
            "var_name": "occupancy_ratio",
            "data_column_name": "Occupancy[perimeter_zn_1]",
            "local_var_name": "occupancy_ratio",
        })

       # Setpoints

        self.variables.append({
            "type": "tvp",
            "data_source": "modeldata",
            "var_name": "TSetpoint_Lower",
            "data_column_name": "LowerSetp[perimeter_zn_1]",
            "local_var_name": "tsetpoint_lower",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "modeldata",
            "var_name": "TSetpoint_Upper",
            "data_column_name": "UpperSetp[perimeter_zn_1]",
            "local_var_name": "tsetpoint_upper",
        })

        # Costs

        self.variables.append({
            "type": "tvp",
            "data_source": "prices",
            "var_name": "ElecCost",
            "data_column_name": "PriceElectricPowerConstant",
            "local_var_name": "elec_cost",
        })

        # running configuration
        self.time_step = 300
        self.length = 24 * 3600 * 1
        self.n_horizon = int(8 * 3600 / self.time_step)

        # Revert to this start time when generating final datset
        self.start_time = 3 * 24 * 60 * 60  # 3 days * 24 hours * 60 minutes * 60 seconds -- start of day 4.
        self.start_time_dt = datetime.datetime(2020, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=self.start_time)  # datetime obj represenation of start time
        self.start_time_offset = self.start_time

        self.tvp_template = None
        self.tvp_template_mhe = None
        self.tvp_template_simulator = None

        # resample if necessary
        self.prices = self.prices.resample(str(self.time_step)+'S').pad()
        self.weather = self.weather.resample(str(self.time_step) + 'S').interpolate()
        self.modeldata = self.modeldata.resample(str(self.time_step) + 'S').pad()

    def tvp_fun(self, t_now):
        if self.tvp_template is None:
            raise Exception("Need to set tvp_template in the ModelParameters instance.")

        ind = int((self.start_time_offset + t_now) / self.time_step)

        # populate all of the time varying parameters
        for var in self.variables:
            # determine which datafile to use
            if var["data_source"] == "weather":
                data_source = self.weather
            elif var["data_source"] == "prices":
                data_source = self.prices
            elif var["data_source"] == "modeldata":
                data_source = self.modeldata
            elif var["data_source"] == "extras":
                data_source = self.extras
            else:
                raise Exception("Missing 'data_source' in model_parameter column definition dictionary")

            # The data need to be passed as a list of array elements (so list of np.array([d]))
            # The length is n_horizon + 1.
            loaded_data = data_source[var["data_column_name"]].values[ind:ind + self.n_horizon + 1]

            self.tvp_template["_tvp", :, var["var_name"]] = [np.array([d]) for d in loaded_data]

        return self.tvp_template

    def tvp_fun_mhe(self, t_now):
        if self.tvp_template_mhe is None:
            raise Exception("Need to set tvp_template_mhe in the ModelParameters instance.")

        ind = int((self.start_time_offset + t_now) / self.time_step)

        # populate all of the time varying parameters
        for var in self.variables:
            if var["data_source"] == "weather":
                data_source = self.weather
            elif var["data_source"] == "prices":
                data_source = self.prices
            elif var["data_source"] == "modeldata":
                data_source = self.modeldata
            elif var["data_source"] == "extras":
                data_source = self.extras
            else:
                raise Exception("Missing 'data_source' in model_parameter column definition dictionary")

            # The data need to be passed as a list of array elements (so list of np.array([d]))
            # The length is n_horizon + 1.
            loaded_data = data_source[var["data_column_name"]].values[ind:ind + self.n_horizon + 1]

            self.tvp_template_mhe["_tvp", :, var["var_name"]] = [np.array([d]) for d in loaded_data]

        return self.tvp_template_mhe

    def tvp_fun_simulator(self, t_now):
        if self.tvp_template_simulator is None:
            raise Exception("Need to set tvp_template_simulator in the ModelParameters instance.")

        ind = int((self.start_time_offset + t_now) / self.time_step)

        # populate all of the time varying parameters
        for var in self.variables:
            # determine which datafile to use
            if var["data_source"] == "weather":
                data_source = self.weather
            elif var["data_source"] == "prices":
                data_source = self.prices
            elif var["data_source"] == "modeldata":
                data_source = self.modeldata
            elif var["data_source"] == "extras":
                data_source = self.extras
            else:
                raise Exception("Missing 'data_source' in model_parameter column definition dictionary")

            # The data need to be passed as a list of array elements (so list of np.array([d]))
            # The length is n_horizon + 1.
            loaded_data = data_source[var["data_column_name"]].values[ind:ind + self.n_horizon + 1]

            # For the simulator case only return a single value
            self.tvp_template_simulator[var["var_name"]] = loaded_data[0]

            # print(f"Verifying timestamp of {data_source['datetime'].values[ind]}")

        return self.tvp_template_simulator


def toEpoch(a, epoch):
    return a + epoch

def toCelsius():
    return a - 273.15