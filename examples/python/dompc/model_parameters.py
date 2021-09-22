from pathlib import Path

import numpy as np
import pandas as pd
import casadi
import datetime


class ModelParameters:
    """This class will be instantiated in various models, so make sure that there are no
    data intensive operations in it."""

    def __init__(self):
        # Load in the N4SID matrices
        p = Path('.').resolve().parent / 'lasso_and_n4sid' / 'n4sid_v10'
        if p.exists():
            # States are room temperatures, <to flesh out>
            self.a = np.load(p / 'output' / 'matrix_A1.npy')
            print(self.a)
            self.b = np.load(p / 'output' / 'matrix_B1.npy')
            print("B Matrix")
            print(self.b.shape)
            print(self.b)
            self.c = np.load(p / 'output' / 'matrix_C1.npy')
            # D array is zeroed out for the length of the inputs in _u
            self.d = np.array([[0, 0, 0, 0, 0]])
            print("D Matrix")
            print(self.d.shape)
            print(self.d)
            self.K = np.load(p / 'output' / 'kalman_gain_K.npy')
            # use the last column of the data per Thibault's comment
            self.x0 = np.transpose([np.load(p / 'output' / 'sys_id1_x0.npy')[:,1]])
            print(self.x0.shape)
            print(self.x0)
            print("finished loading matrices")

            # TODO: need to write a check to make sure these files exist.. someday
            # if not tvp_file.exists():
            #     raise Exception("There is no time varying parameter file, make sure to unzip wrapped 2.7z")

            self.u1test = pd.read_csv(p / 'output' / 'u1test.csv')

            # # Read in the time varying parameters -- old processing code
            # tvp_data = pd.read_csv(tvp_file)
            # df = pd.DataFrame(tvp_data)
            # # only save the samples of 300 seconds
            # df = df.loc[df['Time'] % 300.0 == 0]
            # self.tvp_data = df.drop_duplicates(subset=['Time'])
            # # just temporary -- save off the first 3 months of data to a file to make
            # it easier to inspect
            # self.tvp_data = self.tvp_data.head(int(7000000 / 300))
            # self.tvp_data.to_csv('tmp_exogenous_data.csv')

            p_data = p.resolve() / 'output' / 'u1test_tvps.xls'
            if not p_data.exists():
                raise Exception(f"There is not time varying setpoint parameter file, make sure it exists {p_data}")

            data = pd.read_excel(p_data)
            self.tvp_data = pd.DataFrame(data)

            # print(self.u1test['mod.building.weaBus.TDryBul'].values[0:100])
            # raise SystemExit()
        else:
            raise Exception(f"lasso_and_n4sid path does not exist at {p}")

        # print(f"A: {self.a.shape}")
        # print(f"B: {self.b.shape}")
        # print(f"C: {self.c.shape}")
        # print(f"D: {self.d.shape}")

        # Additional states
        #   --  Initial T Zn1, Initial Heating Power Zn1, Previous Heating Power Zn1
        self.additional_x_states_inits = np.array([[293], [0], [0]])

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
        # self.min_oa_damp_1 = 0.25
        # self.max_oa_damp_1 = 1
        self.min_fan_power = 0
        self.max_fan_power = 1

        # state space u values
        # u[0]  = 't_dry_bulb'
        # u[1]  = 'GloHorRadr'
        # u[2]  = 'Occupancy Ratio'
        # u[3]  = 'Theat_sp - Tzone(t-1)'
        # u[4]  = 'Tzone(t-1) - Tcool_sp'
        # u[5]  = 'Toa(t) - Tzone(t-1)'
        # u[6]  = 'Tzone(t-1) - Tzone(t-2)'
        # u[7]  = 'Tzone(t-1) - Tcool_sp'
        # u[8]  = 'Toa(t) - Tzone(t-1)'
        # u[9]  = 'Tzone(t-1) - Tzone(t-2)'

        # These are the variables that are needed to define the u matrix.
        self.variables = []
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test",
            "var_name": "TDryBul",
            "data_column_name": "T_OA",
            "local_var_name": "t_dry_bulb",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test",
            "var_name": "HGloHor",
            "data_column_name": "HgloHor1",
            "local_var_name": "h_glo_hor",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test",
            "var_name": "occupancy_ratio",
            "data_column_name": "P1_OccN",
            "local_var_name": "occupancy_ratio",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test",
            "var_name": "P1_IntGaiTot",
            "data_column_name": "P1_IntGaiTot",
            "local_var_name": "P1_IntGaiTot",
        })
        # self.variables.append({
        #     "type": "tvp",
        #     # "data_source": "tvp_setpoint_data",
        #     "data_source": "u1test",
        #     "var_name": "P1_HeaPow",
        #     "data_column_name": "P1_HeaPow",
        #     "local_var_name": "P1_HeaPow",
        # })
        # self.variables.append({
        #     "type": "tvp",
        #     "data_source": "u1test",
        #     "var_name": "P1_FanPow",
        #     "data_column_name": "P1_FanPow",
        #     "local_var_name": "P1_FanPow",
        # })
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test",
            "var_name": "OAVent",
            "data_column_name": "P1_OAVol",
            "local_var_name": "oa_vent",
        })

        # tvp_setpoint_data
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test_tvps",
            "var_name": "TSetpoint_Lower",
            "data_column_name": "tsetpoint_lower",
            "local_var_name": "tsetpoint_lower",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test_tvps",
            "var_name": "TSetpoint_Upper",
            "data_column_name": "tsetpoint_upper",
            "local_var_name": "tsetpoint_upper",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test_tvps",
            "var_name": "ElecCost",
            "data_column_name": "elec_cost_multiplier",
            "local_var_name": "elec_cost_multiplier",
        })

        # running configuration
        self.time_step = 300
        # TODO: This should be one day once things are working.
        self.n_horizon = 96 #  8 hours ahead  -- 1 hour is 12 steps in the horizon

        # Revert to this start time when generating final datset
        self.start_time = 3 * 24 * 60 * 60  # 3 days * 24 hours * 60 minutes * 60 seconds -- start of day 4.
        self.start_time_dt = datetime.datetime(2020, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=self.start_time)  # datetime obj represenation of start time
        self.start_time_offset = 0

        # start closer to when occupancy with start
        # 280800 == 1/4/20 06:00
        # self.start_time = 280800
        # if the datafiles are not starting at the same time as `start_time` then pass in an offest to
        # jump to the right index. Start_time - first row of data time (in seconds)
        # self.start_time_offset = 280800 - 259200

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
            if var["data_source"] == "u1test":
                data_source = self.u1test
            elif var["data_source"] == "u1test_tvps":
                data_source = self.tvp_data
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
            if var["data_source"] == "u1test":
                data_source = self.u1test
            elif var["data_source"] == "u1test_tvps":
                data_source = self.tvp_data
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
            if var["data_source"] == "u1test":
                data_source = self.u1test
            elif var["data_source"] == "u1test_tvps":
                data_source = self.tvp_data
            else:
                raise Exception("Missing 'data_source' in model_parameter column definition dictionary")

            # The data need to be passed as a list of array elements (so list of np.array([d]))
            # The length is n_horizon + 1.
            loaded_data = data_source[var["data_column_name"]].values[ind:ind + self.n_horizon + 1]

            # For the simulator case only return a single value
            self.tvp_template_simulator[var["var_name"]] = loaded_data[0]

            # print(f"Verifying timestamp of {data_source['datetime'].values[ind]}")

        return self.tvp_template_simulator

