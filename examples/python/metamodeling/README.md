# Small Office metamodel example

This example shows how to generate a five-zone metamodel for the Small Office model using N4SID.
The framework will simulate a spawn model using the ACTB, record the data, split it into a training and testing dataset,
and attempt to identify a model. 

# Usage

To extract a model, first import the `Metamodel` class from `metamodeling.py` found in the `metamodeling` folder.
Then, instantiate a Metamodel object using `meta = Metamodel(step = 300, config=config, method='N4SID')`, where `step`
is the simulation step, `config` is the metamodel configuration file (explained below) and `method` is the extraction method.
Currently, only N4SID is available, but we will expand this framework to linear methods and classification and regression trees.

Then, generate a metamodel using `meta.generate_matrices(generatedata=True, modelselection='')`. If no data is available, use `generatedata=True`. 
Select the model selection method using `modelselection`. The available methods are best subset selection `"BSS"`, forward stepwise selection `"FSS"`, 
and all available model predictors using an empty string `""`.

# Configuration file

You need to define the following parameters in a separate configuration file. An example is shown in `config_full.py`.

- `metamodel` is the name of the test case you wish to extract a metamodel from, such as `spawnrefsmalloffice`
- `url` is the ACTB's web interface URL, typically `http://127.0.0.1:80`
- `start` is the starting date, in the YY/MM/DD HH:MM:SS format
- `training` is a dictionary that contains the training starting time and length in seconds, and the proportions of time
that the model will be simulated in free floating mode (no controls), rule-based mode, and randomized controls. This allows 
the user to generate a variety of data points that explore the state space extensively.
- `sensors` are the metamodel inputs extracted from the Spawn simulation, they must respect the same naming as the Spawn sensors.
- `outputs` are the outputs that need to be identified, they must respect the same naming as the Spawn model outputs and include a `min` and `max` value.
- `inputs` are the inputs that you wish to use to control the metamodel, they must respect the same naming as the Spawn model and include the type of input (`float` or `bool`) and its `min` and `max` bounds.
- `forecasts` are the time-varying parameters that you wish to include in the metamodel inputs. 
These can come from any .csv file included in the test case resources, such as occupancy or weather data.
- `deactivate` are the controls that you want to deactivate during model identification. For example here, the cooling 
coils are deactivated to prevent the underlying rule-based controller from interfering with the random setpoints chosen by the metamodeling framework.

