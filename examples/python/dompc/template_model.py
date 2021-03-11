# N4SID state space model. Built using Sippy.

from pathlib import Path

from casadi.tools import *

sys.path.append('../')
import do_mpc

# Load in the N4SID matrices
p = Path('.').resolve().parent / 'lasso_and_n4sid'

if p.exists():
    a_matrix = np.load(p / 'matrix_A1.npy')
    b_matrix = np.load(p / 'matrix_B1.npy')
    c_matrix = np.load(p / 'matrix_C1.npy')
    d_matrix = np.load(p / 'matrix_D1.npy')


def template_model():
    model = do_mpc.model.Model('discrete')

    # States are room temperatures, <to flesh out>

    # States struct (optimization variables):
    _x = model.set_variable(var_type='_x', var_name='x', shape=(4, 1))

    # Input struct (optimization variables):
    _u = model.set_variable(var_type='_u', var_name='u', shape=(1, 1))

    # Set expression. These can be used in the cost function, as non-linear constraints
    # or just to monitor another output.

    # how do we make the cost function be a LASSO regression (or any other function?)
    # something like: model.set_expression(expr_name='cost', expr=sum1((_x[1] - _u[1]) ** 2))
    model.set_expression(expr_name='cost', expr=sum1(_x ** 2))

    A = np.array([[0.763, 0.460, 0.115, 0.020],
                  [-0.899, 0.763, 0.420, 0.115],
                  [0.115, 0.020, 0.763, 0.460],
                  [0.420, 0.115, -0.899, 0.763]])

    B = np.array([[0.014],
                  [0.063],
                  [0.221],
                  [0.367]])

    x_next = A @ _x + B @ _u
    model.set_rhs('x', x_next)

    model.setup()

    return model
