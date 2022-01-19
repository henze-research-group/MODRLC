# Spawn data extraction tools

This directory contains utilities for extracting data from EnergyPlus IDFs and generate .CSV files used in Spawn models. 
To see an example of how the tools are used, inspect the `generate_spawndata.py` files present in each test case directory.

## Data generated using extract_data.py

`extract_data.py` is used to load an IDF and an .EPW file and extract the following datasets, used by spawn:
- `dataFromModel.csv` contains information on temperature and IAQ setpoints as well as internal gains.
- `prices.csv` contains pricing scenarios extracted from EnergyPlus tariffs. Warning: this section is a WIP.
- `emissions.csv` contains emission factors for all power sources in the IDF.
- `extras.csv` contains customized extra information not strictly needed by Spawn, but rather by controllers. Currently,
it includes electric loads and target demand limits for developing demand-response scenarios.