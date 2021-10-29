# N4SID and Lasso Regression

This directory contains the scripts to generate the metamodels
needed for the MPC planning model and the RL training model. The
metamodels run much faster than a full modelica simulation and
allow for rapid exploration of the model parameter space.

## Running Instructions

The setup is self-contained and afeter installing the python 
dependencies using Poetry `pip install poetry; poetry install`,
the user can simply run the block below to retrain the metamodels.

```bash
python run.py
```
