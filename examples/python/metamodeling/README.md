# Metamodeling with SIPPY (N4SID and Lasso Regression)

This directory contains the scripts to generate the metamodels
needed for the MPC planning model and the RL training model. The
metamodels run much faster than a full modelica simulation and
allow for rapid exploration of the model parameter space.

Find SIPPY here: https://github.com/CPCLAB-UNIPI/SIPPY.git

## Running Instructions

```bash
python spawnrefsmalloffice.py
```
## Work in progress

- reorganize the model parameter file
- enable saving several metamodels and later selecting them in the various controllers. Right now, we can only use one model at once.
- add license, reference, etc. for SIPPY, as it is not installable with pip and we copied the source in ./resources
