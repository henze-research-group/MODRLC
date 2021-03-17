# Simulation of the model
import sys

sys.path.append('../')
# import do_mpc
from boptest_simulator.boptest_simulator import BoptestSimulator
from template_model import ModelParameters


def template_simulator(model):
    # Currently the simulator is using the same state space model as the planning model.
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
    p_template_sim = simulator.get_p_template()
    def p_fun_mpc(t_now):
        p_template_sim["QCon_flow"] = 1500
        p_template_sim["fanP"] = 250
        p_template_sim["volSenSupV_flow"] = 0.40
        p_template_sim["volSenOAV_flow"] = 0.0009
        p_template_sim["room_relHum"] = 0.50
        p_template_sim["T_supply"] = 295
        return p_template_sim
    simulator.set_p_fun(p_fun_mpc)

    simulator.setup()

    return simulator
