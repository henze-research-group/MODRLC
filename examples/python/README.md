# MODRLC Example Python Controllers

This folder contains controller examples for the ACTB test cases.
At this time, two scenarios are available:
- a demand-response event with two example controllers: a MPC and a RBC. They are available in the `Demand-response` folder.
- a simple scenario with three example controllers: a RLC, a MPC and a RBC. They are available in the `Single-zone` folder/

This folder also contains a usage example for the metamodeling framework, found in the `metamodeling` folder.

Finally, the `BuildingPortfolio` folder shows how to setup the ACTB for simulating several buildings at the same time,
for developing multi-building scenarios.

Please refer to the documentation available in each folder for more details.

## (TODO: cleanup)Installing Dependencies
This project uses poetry to manage dependencies since Alfalfa-client is setup to use Poetry.

```bash
pip install poetry
poetry install
```
