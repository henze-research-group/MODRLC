# MODRLC Example Python Controllers

This folder contains controller examples for the ACTB test cases.
Currently, the following examples are available:
- one rule-based controller for the Spawn small office building. It is located in the ``RBC-spawnrefsmalloffice`` folder
- one model predictive controller for the Spawn small office building. It is located in the ``MPC-spawnrefsmalloffice`` folder
- one reinforcement learning controller for the Spawn small office building. It is located in the ``RLC-spawnrefsmalloffice`` folder

Please refer to the documentation available in each folder for details on the controllers
and their usage.

## (TODO: cleanup)Installing Dependencies
This project uses poetry to manage dependencies since Alfalfa-client is setup to use Poetry.

```bash
pip install poetry
poetry install
```
