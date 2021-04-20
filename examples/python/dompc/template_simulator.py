# Simulation of the model
import sys
import requests
import urllib3

sys.path.append('../')
# import do_mpc
from pathlib import Path
from boptest_simulator.boptest_simulator import BoptestSimulator
from template_model import ModelParameters

sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'boptest_client'))
from boptest_client import BoptestClient


def template_simulator(model):
    # Check if BOPTEST is up and running, if not, then default to just using the state-space
    # equations.

    try:
        client = BoptestClient('http://localhost:5000')
        if client.name() is not None:
            print("BOPTEST is configured to act as simulator")
        else:
            print("Defaulting to simulator=model")
            client = None
    except (requests.exceptions.ConnectionError, urllib3.exceptions.NewConnectionError,):
        print("BOPTEST is not running, if desired launch BOPTEST using `make run TESTCASE=som3`")
        print("Will continue in simulator=model mode")
        client = None

    if client is not None:
        simulator = BoptestSimulator(model, client)
    else:
        simulator = BoptestSimulator(model)

    mp = ModelParameters()

    # simulator.set_param(t_step=0.5)
    # We are running the MPC model at t=300 seconds (5 min).
    simulator.set_param(t_step=mp.time_step)

    tvp_template = simulator.get_tvp_template()
    def tvp_fun(t_now):
        return tvp_template
    simulator.set_tvp_fun(tvp_fun)

    # Testing the parameter configuration
    # p_template_sim = simulator.get_p_template()
    # def p_fun_mpc(t_now):
    #     p_template_sim["QCon_flow"] = 1500
    #     p_template_sim["fanP"] = 250
    #     p_template_sim["volSenSupV_flow"] = 0.40
    #     p_template_sim["volSenOAV_flow"] = 0.0009
    #     p_template_sim["room_relHum"] = 0.50
    #     p_template_sim["T_supply"] = 295
    #     return p_template_sim
    # simulator.set_p_fun(p_fun_mpc)

    simulator.setup()

    return simulator
