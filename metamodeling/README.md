# Stay tuned for an updated guide.

# Metamodeling with SIPPY (N4SID and Lasso Regression)

This directory contains the scripts to generate the metamodels
needed for the MPC planning model and the RL training model. The
metamodels run much faster than a full modelica simulation and
allow for rapid exploration of the model parameter space.

Find SIPPY here: https://github.com/CPCLAB-UNIPI/SIPPY.git

## Running Instructions

The setup is self-contained, simply run `pip install poetry; poetry install`.

To generate a metamodel using N4SID, follow the instructions found in `examples/python/metamodeling/README.md`.

## Work in progress
- add method for online re-training
- add license, reference, etc. for SIPPY

