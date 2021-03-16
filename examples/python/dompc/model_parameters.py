from pathlib import Path

import numpy as np
import pandas as pd


class ModelParameters:
    """This class will be instantiated in various models, so make sure that there are no
    data intensive operations in it."""

    def __init__(self):
        # Load in the N4SID matrices
        p = Path('.').resolve().parent / 'lasso_and_n4sid'
        if p.exists():
            # States are room temperatures, <to flesh out>
            self.a = np.load(p / 'matrix_A1.npy')
            self.b = np.load(p / 'matrix_B1.npy')
            self.c = np.load(p / 'matrix_C1.npy')
            self.d = np.load(p / 'matrix_D1.npy')

            # Read in the time varying parameters
            p_data = Path(p / 'wrapped 2.csv')
            if not p_data.exists():
                raise Exception("There is no time varying parameter file, make sure to unzip wrapped 2.7z")

            data = pd.read_csv(p_data)
            df = pd.DataFrame(data)
            # print(df['Time'])
            # only save the samples of 300 seconds
            df = df.loc[df['Time'] % 300.0 == 0]
            self.tvp_data = df.drop_duplicates(subset=['Time'])

            # print(self.tvp_data['mod.building.weaBus.TDryBul'].values[0:30])
            # raise SystemExit()
            # print(df.columns)
        else:
            raise Exception(f"lasso_and_n4sid path does not exist at {p}")

        # print(f"A: {self.a.shape}")
        # print(f"B: {self.b.shape}")
        # print(f"C: {self.c.shape}")
        # print(f"D: {self.d.shape}")

        # The x matrix is generated by Sippy, we don't know the meaning of the inputs.
        self.max_x = np.array([
            [10.0], [10.0], [10.0], [10.0], [10.0], [10.0], [10.0], [10.0]
        ])
        self.min_x = - self.max_x

        # state space u values
        # u[0]  = 'mod.building.weaBus.HDifHor'
        # u[1]  = 'mod.building.weaBus.HDirNor'
        # u[2]  = 'mod.building.weaBus.HGloHor'
        # u[3]  = 'mod.building.weaBus.HHorIR'
        # u[4]  = 'mod.building.weaBus.TBlaSky'
        # u[5]  = 'mod.building.weaBus.TDryBul'
        # u[6]  = 'mod.building.weaBus.TWetBul'
        # u[7]  = 'mod.building.weaBus.winSpe'
        # u[8]  = 'mod.building.weaBus.winDir'
        # u[9]  = 'mod.building.weaBus.relHum'
        # u[10] = 'mod.corZon.fmuZon.QCon_flow'
        # u[11] = 'mod.HVAC.hea.Q_flow'
        # u[12] = 'mod.HVAC.fan.P'
        # u[13] = 'mod.HVAC.volSenSup.V_flow'
        # u[14] = 'mod.HVAC.volSenOA.V_flow'
        # u[15] = 'mod.HVAC.senRelHum.phi'
        # u[16] = 'mod.HVAC.senTSup.T'
        # These are the variables that are needed to define the u matrix.
        # The order is
        self.variables = []
        self.variables.append({
            "type": "tvp",
            "var_name": "HDifHor",
            "data_column_name": "mod.building.weaBus.HDifHor",
            "plot_axis": 2,
            "local_var_name": "h_dif_hor",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "HDirNor",
            "data_column_name": "mod.building.weaBus.HDirNor",
            "plot_axis": 2,
            "local_var_name": "h_dir_nor",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "HGloHor",
            "data_column_name": "mod.building.weaBus.HGloHor",
            "plot_axis": 2,
            "local_var_name": "h_glo_hor",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "HHorIR",
            "data_column_name": "mod.building.weaBus.HHorIR",
            "plot_axis": None,
            "local_var_name": "h_hor_ir",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "TBlaSky",
            "data_column_name": "mod.building.weaBus.TBlaSky",
            "plot_axis": None,
            "local_var_name": "t_bla_sky",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "TDryBul",
            "data_column_name": "mod.building.weaBus.TDryBul",
            "plot_axis": 1,
            "local_var_name": "t_dry_bulb",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "TWetBul",
            "data_column_name": "mod.building.weaBus.TWetBul",
            "plot_axis": 1,
            "local_var_name": "t_wet_bul",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "winSpe",
            "data_column_name": "mod.building.weaBus.winSpe",
            "plot_axis": None,
            "local_var_name": "win_speed",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "winDir",
            "data_column_name": "mod.building.weaBus.winDir",
            "plot_axis": None,
            "local_var_name": "win_dir",
        })
        self.variables.append({
            "type": "tvp",
            "var_name": "relHum",
            "data_column_name": "mod.building.weaBus.relHum",
            "plot_axis": None,
            "local_var_name": "oa_rel_hum",
        })
        self.max_u = np.array([
            [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0],
            [4.0], [4.0]
        ])
        self.min_u = - self.max_u

        # running configuration
        self.time_step = 300
        self.n_horizon = 30

        self.tvp_template = None

        # ------------------------------------------------------------
        # Example matrices
        # self.a = np.array([[0.763, 0.460, 0.115, 0.020],
        #               [-0.899, 0.763, 0.420, 0.115],
        #               [0.115, 0.020, 0.763, 0.460],
        #               [0.420, 0.115, -0.899, 0.763]])
        #
        # self.b = np.array([[0.014],
        #               [0.063],
        #               [0.221],
        #               [0.367]])
        #
        # # state space max x values
        # self.max_x = np.array([[4.0], [10.0], [4.0], [10.0]])
        # self.min_x = - self.max_x
        #
        # # state space max u values
        # self.min_u = -0.5
        # self.max_u = 0.5
        #
        # # running configuration
        # self.time_step = 300
        # self.n_horizon = 7

    def tvp_fun(self, t_now):
        if self.tvp_template is None:
            raise Exception("Need to set tvp_template in the ModelParameters instance.")

        ind = int(t_now / self.time_step)

        # populate all of the time varying parameters
        for var in self.variables:
            # The data need to be passed as a list of array elements (so list of np.array([d]))
            # The length is n_horizon + 1.
            loaded_data = self.tvp_data[var["data_column_name"]].values[ind:ind + self.n_horizon + 1]
            self.tvp_template["_tvp", :, var["var_name"]] = [np.array([d]) for d in loaded_data]

        return self.tvp_template
