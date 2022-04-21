# MODRLC Example Python Controllers

This folder contains controller examples for the ACTB test cases.
Currently, the following examples are available:
- two rule-based controllers for the Spawn small office building. They are located in the ``RBC-spawnrefsmalloffice`` and ``RBC-spawnrefsmalloffice-DRevent`` folders
- one model predictive controller for the Spawn small office building. It is located in the ``MPC-spawnrefsmalloffice-DRevent`` folder
- one reinforcement learning controller for the Spawn small office building. It is located in the ``RLC-spawnrefsmalloffice`` folder

Please refer to the documentation available in each folder for details on the controllers
and their usage.

## (TODO: cleanup)Installing Dependencies
This project uses poetry to manage dependencies since Alfalfa-client is setup to use Poetry.

```bash
pip install poetry
poetry install
```
