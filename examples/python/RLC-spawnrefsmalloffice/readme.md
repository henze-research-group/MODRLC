# rl example

This folder contains an implementation of the DQN agent with experience replay controlling the low-level heating coil power. 

To run the RL problem that is contained in this folder, do the following.

* In the [python folder](../) (on up from this one), install the dependencies using Poetry. The instructions are
  in that folder's [REAMDE file](../README.md).

* In a seperate terminal launch the testcase from the project checkout base directory. The `spawnrefsmalloffice` model is the only one that this controller has been tested with. 

  * `make run`
  
* Run the `DQN_Test_run.py` file in this folder to run the RL agent. 

  ```bash
  python3 DQN_Test_run.py  
  ```
