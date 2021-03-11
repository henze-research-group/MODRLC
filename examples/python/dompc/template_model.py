# N4SID state space model. Built using Sippy.

from pathlib import Path

from casadi.tools import *

sys.path.append('../')
import do_mpc




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

        print(self.a.shape)
        print(self.b.shape)

        # TODO: list what these state variables are
        self.max_x = np.array([
            [4.0], [10.0], [4.0], [10.0], [4.0], [10.0], [4.0], [10.0]
        ])
        self.min_x = - self.max_x

        # state space max u values
        # TODO: list the control variables here
        self.max_u = np.array([
            [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0], [4.0]
        ])
        self.min_u = - self.max_u

        # running configuration
        self.time_step = 300
        self.n_horizon = 30

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


def template_model():
    model = do_mpc.model.Model('discrete')

    mp = ModelParameters()

    # States struct (optimization variables):
    # x's shape is the A's num of columns x 1
    _x = model.set_variable(var_type='_x', var_name='x', shape=(mp.a.shape[1], 1))

    # Input struct (optimization variables):
    # u's shape is B's num of columns x 1
    _u = model.set_variable(var_type='_u', var_name='u', shape=(mp.b.shape[1], 1))

    # Set expression. These can be used in the cost function, as non-linear constraints
    # or just to monitor another output.

    # how do we make the cost function be a LASSO regression (or any other function?)
    # something like: model.set_expression(expr_name='cost', expr=sum1((_x[1] - _u[1]) ** 2))
    model.set_expression(expr_name='cost', expr=sum1(_x ** 2))

    x_next = mp.a @ _x + mp.b @ _u
    model.set_rhs('x', x_next)

    model.setup()

    return model
