from pathlib import Path

import numpy as np
import pandas as pd


class ModelParameters:
    """This class will be instantiated in various models, so make sure that there are no
    data intensive operations in it."""

    def __init__(self):
        # Load in the N4SID matrices
        p = Path('.').resolve().parent / 'lasso_and_n4sid' / 'n4sid_v4'
        if p.exists():
            # States are room temperatures, <to flesh out>
            self.a = np.load(p / 'matrix_AK1.npy')
            self.b = np.load(p / 'matrix_BK1.npy')
            self.c = np.load(p / 'matrix_C1.npy')
            self.d = np.load(p / 'matrix_D1.npy')

            # Read in the time varying parameters
            p_data = Path(p.parent / 'wrapped 2.csv')
            if not p_data.exists():
                raise Exception("There is no time varying parameter file, make sure to unzip wrapped 2.7z")

            data = pd.read_csv(p_data)
            df = pd.DataFrame(data)
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

            # print(self.tvp_data['mod.building.weaBus.TDryBul'].values[0:30])
            # raise SystemExit()
            # print(df.columns)
        else:
            raise Exception(f"lasso_and_n4sid path does not exist at {p}")

        # print(f"A: {self.a.shape}")
        # print(f"B: {self.b.shape}")
        # print(f"C: {self.c.shape}")
        # print(f"D: {self.d.shape}")

        self.min_x = np.array([-10.0])
        self.max_x = np.array([10.0])
        # The x matrix is generated by Sippy
        # self.min_x = np.array([[-1.5], [-1.0], [-1.5]])
        # self.max_x = np.array([[ 0.0], [ 0.5], [ 1.5]])

        # Indoor temperature bounds
        self.min_indoor_t = np.array([250])
        self.max_indoor_t = np.array([310])

        self.min_setpoint_t = np.array([293])
        self.max_setpoint_t = np.array([298])

        self.min_heating = 0
        self.min_cooling = 0
        self.max_heating = 14000
        self.max_cooling = 7000

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
            "var_name": "TDryBul",
            "data_column_name": "mod.building.weaBus.TDryBul",
            "plot_axis": 2,
            "local_var_name": "t_dry_bulb",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "HGloHor",
            "data_column_name": "mod.building.weaBus.HGloHor",
            "plot_axis": 3,
            "local_var_name": "h_glo_hor",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvp_setpoint_data",
            "var_name": "occupancy_ratio",
            "data_column_name": "occupancy_ratio",
            "plot_axis": 7,
            "local_var_name": "occupancy_ratio",
        })
        # tvp_setpoint_data

        self.variables.append({
            "type": "tvp",
            "data_source": "tvp_setpoint_data",
            "var_name": "TSetpoint_Lower",
            "data_column_name": "tsetpoint_lower",
            "plot_axis": 5,
            "local_var_name": "tsetpoint_lower",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvp_setpoint_data",
            "var_name": "TSetpoint_Upper",
            "data_column_name": "tsetpoint_upper",
            "plot_axis": 5,
            "local_var_name": "tsetpoint_upper",
        })
        self.variables.append({
            "type": "tvp",
            "data_source": "tvp_setpoint_data",
            "var_name": "ElecCost",
            "data_column_name": "elec_cost",
            "plot_axis": 6,
            "local_var_name": "elec_cost",
        })

        # running configuration
        self.time_step = 300
        self.n_horizon = 30

        self.tvp_template = None

    def tvp_fun(self, t_now):
        if self.tvp_template is None:
            raise Exception("Need to set tvp_template in the ModelParameters instance.")

        ind = int(t_now / self.time_step)

        # populate all of the time varying parameters
        for var in self.variables:
            # determine which datafile to use
            data_source = None
            if "data_source" in var:
                if var["data_source"] == "tvp_setpoint_data":
                    data_source = self.tvp_setpoint_data
            else:
                data_source = self.tvp_data

            # The data need to be passed as a list of array elements (so list of np.array([d]))
            # The length is n_horizon + 1.
            loaded_data = data_source[var["data_column_name"]].values[ind:ind + self.n_horizon + 1]
            self.tvp_template["_tvp", :, var["var_name"]] = [np.array([d]) for d in loaded_data]

        return self.tvp_template
