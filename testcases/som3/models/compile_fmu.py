#!/usr/bin/env python3
##########################################################################
# Script to simulate Modelica models with JModelica.
#
##########################################################################
# Import the function for compilation of models and the load_fmu method

from pymodelica import compile_fmu
import traceback
import logging

from pyfmi import load_fmu
import pymodelica

import os
import shutil
import sys

debug_solver = False
model="wrapped"
generate_plot = False

# Overwrite model with command line argument if specified
if len(sys.argv) > 1:
  # If the argument is a file, then parse it to a model name
  if os.path.isfile(sys.argv[1]):
    model = sys.argv[1].replace(os.path.sep, '.')[:-3]
  else:
    model=sys.argv[1]


print("*** Compiling {}".format(model))
# Increase memory
pymodelica.environ['JVM_ARGS'] = '-Xmx4096m'


sys.stdout.flush()

######################################################################
# Compile fmu
fmu_name = compile_fmu(model, 'wrapped.mo',
                       version="2.0",
                       compiler_log_level='info', #, 'warning',
                       compiler_options = {"generate_html_diagnostics" : True, "nle_solver_tol_factor": 1e-2})
print(fmu_name)

######################################################################
