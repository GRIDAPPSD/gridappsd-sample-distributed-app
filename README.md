# Sample Distributed Field Bus Application

This repository contains examples of distributed applications and services developed using GridAPPS-D's distributed API. 

1. [Sample Distributed App](https://github.com/GRIDAPPSD/gridappsd-sample-distributed-app/blob/after_test/run_sample_distributed_app.py): It is an example of a distributed application with a Coordinating Agent that spawns distributed agents at Feeder, Switch areas and Secondary areas in a grid network model. It also contains example for discovering near by agents and requesting data from them. 
3. [Sample Distributed App Without Coordinating App](<https://github.com/GRIDAPPSD/gridappsd-sample-distributed-app/blob/after_test/run_sample_distributed_app_without_coord_agent.py>): It is an example of a distributed application that creates distributed agents at Feeder, Switch areas and Secondary areas in a grid network model. 
4. [Sample Distributed Service](https://github.com/GRIDAPPSD/gridappsd-sample-distributed-app/blob/after_test/run_sample_distributed_service.py): It is an example of a distributed service that receives request from near by distributed agents and respond back with sample data.
5. [Context Manager](https://github.com/GRIDAPPSD/gridappsd-sample-distributed-app/blob/after_test/run_context_mananger_agent.py): Context Manager is a distrbuted service that provides contextual information to near by distributed agents such as local area network information, near by agents and devices etc. 

## Configuration

### 1. Configure Simulation Request

These examples can be configured to work with either simulated or real network and measurements. By default, they are configured to work with 13nodeckt network model from gridappsd with 8000 seconds of real time simulation.  You 
can find the following file in [sample-distributed/config_files_simulated/simulation-config.json](config_files_simulated/simulation-config.json) 
should you want to change it.

![Simulation Configuration](images/ieee-13-node-sim.png)

### 2. Provide Authentication Details
Modify [auth_context.py](https://github.com/GRIDAPPSD/gridappsd-sample-distributed-app/blob/after_test/auth_context.py) with the correct values for the different environmental variables.  These will be used
to overwrite the values in the different yaml configuration files for connecting to gridappsd as field bus.

## Steps to Run

### 1. Start GridAPPS-D Platform
In order to run this example you will need to first have GridAPPS-D platform running.  Follow instructions at gridappsd-docker repository.

### 2. Start a Simulation
Open a new command terminals with an environment containing the gridappsd-python version.
```commandline
# Command line 1 holds the simulation running
python run_simulation.py
```

![Run Simulation Output](images/run-simulation-output.png)

### 3. Run Context Manager
Open a new terminal and run the context manager so other distributed agents can discover near by agents, devices and their location in the network.
```commandline
# Command line 1 holds the simulation running
python run_context_manager_agent.py
```

### 4. Run Sample Distributed Service
Open a new terminal and run the sample distributed service so sample app can request data from the service.
```commandline
# Command line 1 holds the simulation running
python run_sample_distributed_service.py
```

### 4. Run Sample Distributed App (with or without coordinating app) 
Open a new terminal and run the sample distributed app either with or without coordinating agents.
```commandline
# Command line 1 holds the simulation running
python run_sample_distributed_app.py
```
OR
```commandline
# Command line 1 holds the simulation running
python run_sample_distributed_app_without_coord_agent.py
```

![Run Distributed App](images/run-distributed-app.png)

You can see the creation and retrieval of all the messages on the different terminals.
