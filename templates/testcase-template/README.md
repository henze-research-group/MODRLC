# Test case template

This guide explains how to set up a test case directory for compiling and simulating your own models in the ACTB.
Each file has a description if possible (except for the JSON files) and its role is otherwise explained here.

## Documentation folder

It is not strictly necessary, the ACTB will not fail if it is not present, but we highly recommend that you keep a trace of the model inputs and outputs.

## Model folder

This folder contains the model resources. It should contain at least the following:

### The Modelica model
This is the .mo file that you created when designing your model. Drop it here, and take note of the model name as specified in the file.

### The compile_fmu.py script
This informs the compiler about the exact model you want to compile. Where appropriate, replace the path to your .mo file and the model name to match your own Modelica model.

### The config.json file
This file contains simulation parameters.
| Input | Description | Effect |
--------|-------------|---------
| name | Test case name | Specifies the name that appears in the Alfalfa simulation manager |
| area | Total building surface in square meters | Certain KPIs are reported in units per square meter |
| start_time | Simulation start time in seconds | Simulation start time |
| warmup_period | Simulation warm-up period in seconds | Simulation warm-up period |
| step | Simulation step in seconds | Simulation step |
| horizon | Forecast horizon in seconds | Sets the length of the forecast horizon |
| interval | Forecast interval in seconds | Sets the interval between forecasts |
| scenario | Pricing scenario | Sets the pricing scenario for economic KPIs |


### The days.json file
This file contains the days of peak cooling and peak heating.

### The library_versions.json file
This is where you should indicate the commit hash of the Modelica libraries you are using.

### The Resources folder
If you are simulating a Spawn model, this folder should contain:
- the original EnergyPlus IDF that you are using
- the .epw weather file, used for generating test case data
- the .mos version of your weather file, used by the Modelica simulation engine

