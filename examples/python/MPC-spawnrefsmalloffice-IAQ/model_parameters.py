from pathlib import Path

import numpy as np
import pandas as pd
import datetime


class ModelParameters:
    """This class will be instantiated in various models, so make sure that there are no
    data intensive operations in it."""

    def __init__(self):

        # running configuration
        self.time_step = 300
        self.length = 24 * 3600 * 1
        self.n_horizon = int(3 * 3600 / self.time_step)  # 8 hours ahead  -- 1 hour is 12 steps in the horizon

        # Revert to this start time when generating final datset
        self.start_time = 3 * 24 * 60 * 60  # 3 days * 24 hours * 60 minutes * 60 seconds -- start of day 4.
        self.start_time_dt = datetime.datetime(2017, 1, 1, 0, 0, 0) + datetime.timedelta(
            seconds=self.start_time)  # datetime obj represenation of start time
        self.start_time_offset = self.start_time

        # Load in the N4SID matrices
        p = Path('').resolve().parent.parent.parent / 'testcases' / 'SpawnResources' / 'spawnrefsmalloffice' / 'metamodels' / 'N4SID-TempsOnly'
        if p.exists():
            # States are room temperatures, <to flesh out>
            self.a = np.load(p / 'A.npy')
            self.b = np.load(p / 'B.npy')
            self.c = np.load(p / 'C.npy')
            # D array is zeroed out for the length of the inputs in _u
            self.d = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
            self.K = np.load(p / 'K.npy')
            # use the last column of the data per Thibault's comment
            self.x0 = np.transpose([np.load(p / 'x0.npy')])
            #input("Are you happy with this X? {}".format(self.x0.shape))
            self.k1 = 63.3820598#np.matrix([63.3820598]*5)
            self.k2 = 0.813545658#np.matrix([0.813545658]*5)
            self.k3 = 271.14357#np.matrix([271.14357]*5)
            self.k4 = 0.814834210#np.matrix([0.814834210]*5)
            self.k5 = 5067.28855#np.matrix([5067.28855]*5)
            self.k6 = 17253.1871#np.matrix([17253.1871]*5)
            self.oaco2 = 397.5#np.matrix([397.5]*5)

            # TODO: need to write a check to make sure these files exist.. someday
            # if not tvp_file.exists():
            #     raise Exception("There is no time varying parameter file, make sure to unzip wrapped 2.7z")

            self.tvps = pd.read_csv(p.parent.parent / 'dataFromModel.csv')
            self.extras = pd.read_csv(p.parent.parent / 'extras.csv')
            self.weather = pd.read_csv(p.parent.parent / 'weather.csv')

            # resample from E+ hourly data to 'step'
            index = pd.DatetimeIndex(data= pd.date_range(start=datetime.datetime(2017, 1, 1, 0, 0, 0), periods=len(self.extras), freq='H'), freq='H')
            self.tvps.set_index(index, inplace=True)
            self.extras.set_index(index, inplace=True)
            self.weather.set_index(index, inplace=True)
            self.tvps = self.tvps.resample(rule=str(self.time_step) + 'S').pad()
            self.extras = self.extras.resample(rule=str(self.time_step)+'S').pad()
            self.weather = self.weather.resample(rule=str(self.time_step) + 'S').interpolate()


        else:
            raise Exception(f"metamodeling path does not exist at {p}")

        # Additional states
        #   --  Initial T Zn1, Initial Heating Power Zn1, Previous Heating Power Zn1
        self.additional_x_states_inits = np.array(
            [   
                # CO2 concentrations (ppm)
                [400], [400], [400], [400], [400], 
                # Indoor air temperatures (K)
                [293], [293], [293], [293], [293], 
                # Cost function: Current heating coil power
                [0], [0], [0], [0], [0], 
                # Cost function: Previous heating coil power
                #[0], [0], [0], [0], [0], 
                # Cost function: Current damper position
                #[0], [0], [0], [0], [0], 
                # Cost function: Previous damper position
                #[0], [0], [0], [0], [0], 
                # Other cost functions: total demand, elec cost, discomfort, IAQ
                #[0], [0], [0], [0], 
                # Previous change in CO2 due to occupants
                [0], [0], [0], [0], [0],
                # Previous change in CO2 due to ventilation
                [0], [0], [0], [0], [0], 
                # Previous levels of CO2
                #[0], [0], [0], [0], [0],               
                ]
            
            )

        # The min_x is +/- 10 for the number of rows of A which is the # of states
        self.min_x = np.array([[-30]] * self.a.shape[0])
        self.max_x = - self.min_x

        # Indoor temperature bounds
        self.min_indoor_t = np.array([250])
        self.max_indoor_t = np.array([310])

        self.min_setpoint_t = np.array([293])
        self.max_setpoint_t = np.array([298])

        self.min_cooling = 0
        self.max_cooling = 0
        self.min_heating = 0
        self.max_heating = 1
        self.min_oa_damp = 0.0
        self.max_oa_damp = 0.5
        self.min_fan_power = 0
        self.max_fan_power = 1

        # These are the variables that are needed to define the u matrix.
        self.variables = []

        # Weather

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

        # Occupancy

        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "occupancy_ratio_core",
            "data_column_name": "Occupancy[core_zn]",
            "local_var_name": "occupancy_ratio_core",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "occupancy_ratio_perimeter1",
            "data_column_name": "Occupancy[perimeter_zn_1]",
            "local_var_name": "occupancy_ratio_perimeter1",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "occupancy_ratio_perimeter2",
            "data_column_name": "Occupancy[perimeter_zn_2]",
            "local_var_name": "occupancy_ratio_perimeter2",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "occupancy_ratio_perimeter3",
            "data_column_name": "Occupancy[perimeter_zn_3]",
            "local_var_name": "occupancy_ratio_perimeter3",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "occupancy_ratio_perimeter4",
            "data_column_name": "Occupancy[perimeter_zn_4]",
            "local_var_name": "occupancy_ratio_perimeter4",
        })


        # CO2 setpoints

        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "co2_setpoint_core",
            "data_column_name": "UpperCO2[core_zn]",
            "local_var_name": "co2_setpoint_core",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "co2_setpoint_perimeter1",
            "data_column_name": "UpperCO2[perimeter_zn_1]",
            "local_var_name": "co2_setpoint_perimeter1",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "co2_setpoint_perimeter2",
            "data_column_name": "UpperCO2[perimeter_zn_2]",
            "local_var_name": "co2_setpoint_perimeter2",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "co2_setpoint_perimeter3",
            "data_column_name": "UpperCO2[perimeter_zn_3]",
            "local_var_name": "co2_setpoint_perimeter3",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "co2_setpoint_perimeter4",
            "data_column_name": "UpperCO2[perimeter_zn_4]",
            "local_var_name": "co2_setpoint_perimeter4",
        })

        # Electrical loads

        self.variables.append({
            "type": "tvp",
            "data_source": "extras",
            "var_name": "equipment_gains_core",
            "data_column_name": "ElecLoads[core_zn]",
            "local_var_name": "equipment_gains_core",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "extras",
            "var_name": "equipment_gains_perimeter1",
            "data_column_name": "ElecLoads[perimeter_zn_1]",
            "local_var_name": "equipment_gains_perimeter1",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "extras",
            "var_name": "equipment_gains_perimeter2",
            "data_column_name": "ElecLoads[perimeter_zn_2]",
            "local_var_name": "equipment_gains_perimeter2",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "extras",
            "var_name": "equipment_gains_perimeter3",
            "data_column_name": "ElecLoads[perimeter_zn_3]",
            "local_var_name": "equipment_gains_perimeter3",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "extras",
            "var_name": "equipment_gains_perimeter4",
            "data_column_name": "ElecLoads[perimeter_zn_4]",
            "local_var_name": "equipment_gains_perimeter4",
        })


        # Setpoints

        self.variables.append({
            "type": "tvp",
            "data_source": "extras",
            "var_name": "tdl",
            "data_column_name": "tdl",
            "local_var_name": "tdl",
        })

        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "TSetpoint_Lower",
            "data_column_name": "LowerSetp[core_zn]",
            "local_var_name": "tsetpoint_lower",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvps",
            "var_name": "TSetpoint_Upper",
            "data_column_name": "UpperSetp[core_zn]",
            "local_var_name": "tsetpoint_upper",
        })



        self.tvp_template = None
        self.tvp_template_mhe = None
        self.tvp_template_simulator = None

    def tvp_fun(self, t_now):
        if self.tvp_template is None:
            raise Exception("Need to set tvp_template in the ModelParameters instance.")

        ind = int((self.start_time_offset + t_now) / self.time_step)

        # populate all of the time varying parameters
        for var in self.variables:
            # determine which datafile to use
            if var["data_source"] == "tvps":
                data_source = self.tvps
            elif var["data_source"] == "weather":
                data_source = self.weather
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
            # determine which datafile to use
            if var["data_source"] == "tvps":
                data_source = self.tvps
            elif var["data_source"] == "weather":
                data_source = self.weather
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
            if var["data_source"] == "tvps":
                data_source = self.tvps
            elif var["data_source"] == "weather":
                data_source = self.weather
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

