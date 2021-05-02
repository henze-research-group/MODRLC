from pathlib import Path

import numpy as np
import pandas as pd
import casadi


class ModelParameters:
    """This class will be instantiated in various models, so make sure that there are no
    data intensive operations in it."""

    def __init__(self):
        # Load in the N4SID matrices
        p = Path('.').resolve().parent / 'lasso_and_n4sid' / 'n4sid_v6'
        if p.exists():
            # States are room temperatures, <to flesh out>
            self.a = np.load(p / 'output' / 'matrix_A1.npy')
            self.b = np.load(p / 'output' / 'matrix_B1.npy')
            self.c = np.load(p / 'output' / 'matrix_C1.npy')
            self.d = np.load(p / 'output' / 'matrix_D1.npy')
            self.x0 = np.load(p / 'output' / 'sys_id1_x0.npy')
            self.u1test = pd.read_excel(p / 'output' / 'u1test.xlsx')

            # Read in the time varying parameters
            tvp_file = Path(p.parent / 'wrapped 2.csv')
            if not tvp_file.exists():
                raise Exception("There is no time varying parameter file, make sure to unzip wrapped 2.7z")

            tvp_data = pd.read_csv(tvp_file)
            df = pd.DataFrame(tvp_data)
            # only save the samples of 300 seconds
            df = df.loc[df['Time'] % 300.0 == 0]
            self.tvp_data = df.drop_duplicates(subset=['Time'])

            # just temporary -- save off the first 3 months of data to a file to make
            # it easier to inspect
            self.tvp_data = self.tvp_data.head(int(7000000 / 300))
            self.tvp_data.to_csv('tmp_exogenous_data.csv')

            p_data = Path('.').resolve() / 'setpoint_tvp.xlsx'
            if not p_data.exists():
                raise Exception(f"There is not time varying setpoint parameter file, make sure it exists {p_data}")

            data = pd.read_excel(p_data)
            self.tvp_setpoint_data = pd.DataFrame(data)

            # print(self.u1test['mod.building.weaBus.TDryBul'].values[0:100])
            # raise SystemExit()
        else:
            raise Exception(f"lasso_and_n4sid path does not exist at {p}")

        # print(f"A: {self.a.shape}")
        # print(f"B: {self.b.shape}")
        # print(f"C: {self.c.shape}")
        # print(f"D: {self.d.shape}")


        self.min_x = np.array([[-20],[-20], [-20], [-20], [-20]]) #, [-20], [-20]])
        self.max_x = - self.min_x
        # The x matrix is generated by Sippy
        # self.min_x = np.array([[-1.5], [-1.0], [-1.5]])
        # self.max_x = np.array([[ 0.0], [ 0.5], [ 1.5]])

        # Indoor temperature bounds
        self.min_indoor_t = np.array([250])
        self.max_indoor_t = np.array([310])

        self.min_setpoint_t = np.array([293])
        self.max_setpoint_t = np.array([298])

        self.min_cooling = 0
        self.max_cooling = 0
        self.min_heating = 0
        self.max_heating = 6000
        self.min_fan_power = 0
        self.max_fan_power = 500

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
            # "data_source": "tvp_setpoint_data",
            "data_source": "u1test",
            "var_name": "TDryBul",
            "data_column_name": "mod.building.weaBus.TDryBul",
            "local_var_name": "t_dry_bulb",
        })
        self.variables.append({
            "type": "tvp",
            # "data_source": "tvp_setpoint_data",
            "data_source": "u1test",
            "var_name": "HGloHor",
            "data_column_name": "mod.building.weaBus.HGloHor",
            "local_var_name": "h_glo_hor",
        })
        self.variables.append({
            "type": "tvp",
            # "data_source": "tvp_setpoint_data",
            "data_source": "u1test",
            "var_name": "occupancy_ratio",
            "data_column_name": "occupancy_ratio",
            "local_var_name": "occupancy_ratio",
        })
        self.variables.append({
            "type": "tvp",
            # "data_source": "tvp_setpoint_data",
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
        self.variables.append({
            "type": "tvp",
            # "data_source": "tvp_setpoint_data",
            "data_source": "u1test",
            "var_name": "P1_FanPow",
            "data_column_name": "P1_FanPow",
            "local_var_name": "P1_FanPow",
        })
        self.variables.append({
            "type": "tvp",
            # "data_source": "tvp_setpoint_data",
            "data_source": "u1test",
            "var_name": "OAVent",
            "data_column_name": "OAVent",
            "local_var_name": "oa_vent",
        })

        # tvp_setpoint_data
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test",
            "var_name": "TSetpoint_Lower",
            "data_column_name": "tsetpoint_lower",
            "local_var_name": "tsetpoint_lower",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test",
            "var_name": "TSetpoint_Upper",
            "data_column_name": "tsetpoint_upper",
            "local_var_name": "tsetpoint_upper",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "u1test",
            "var_name": "ElecCost",
            "data_column_name": "elec_cost",
            "local_var_name": "elec_cost",
        })

        # running configuration
        self.time_step = 300
        # TODO: This should be one day once things are working.
        self.n_horizon = 100

        self.tvp_template = None

    def tvp_fun(self, t_now):
        if self.tvp_template is None:
            raise Exception("Need to set tvp_template in the ModelParameters instance.")

        ind = int(t_now / self.time_step)

        # populate all of the time varying parameters
        for var in self.variables:
            # determine which datafile to use
            if var["data_source"] == "tvp_setpoint_data":
                data_source = self.tvp_setpoint_data
            elif var["data_source"] == "u1test":
                data_source = self.u1test
            elif var["data_source"] == "tvp_data":
                data_source = self.tvp_data
            else:
                raise Exception("Missing 'data_source' in model_parameter column definition dictionary")

            # The data need to be passed as a list of array elements (so list of np.array([d]))
            # The length is n_horizon + 1.
            loaded_data = data_source[var["data_column_name"]].values[ind:ind + self.n_horizon + 1]

            self.tvp_template["_tvp", :, var["var_name"]] = [np.array([d]) for d in loaded_data]

        return self.tvp_template

    def tvp_fun_simulator(self, t_now):
        if self.tvp_template is None:
            raise Exception("Need to set tvp_template in the ModelParameters instance.")

        ind = int(t_now / self.time_step)

        # populate all of the time varying parameters
        for var in self.variables:
            # determine which datafile to use
            if var["data_source"] == "tvp_setpoint_data":
                data_source = self.tvp_setpoint_data
            elif var["data_source"] == "u1test":
                data_source = self.u1test
            elif var["data_source"] == "tvp_data":
                data_source = self.tvp_data
            else:
                raise Exception("Missing 'data_source' in model_parameter column definition dictionary")

            # The data need to be passed as a list of array elements (so list of np.array([d]))
            # The length is n_horizon + 1.
            loaded_data = data_source[var["data_column_name"]].values[ind:ind + self.n_horizon + 1]

            # For the simulator case only return a single value
            self.tvp_template[var["var_name"]] = loaded_data[0]

        return self.tvp_template

