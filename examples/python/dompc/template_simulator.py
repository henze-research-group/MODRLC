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

    simulator.setup()

    return simulator
