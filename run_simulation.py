import json
import os
from pathlib import Path

from gridappsd import GridAPPSD
from gridappsd.simulation import Simulation

import auth_context

os.environ['GRIDAPPSD_APPLICATION_ID'] = 'dist-sample-sim'
os.environ['GRIDAPPSD_APPLICATION_STATUS'] = 'STARTED'
os.environ['GRIDAPPSD_USER'] = 'app_user'
os.environ['GRIDAPPSD_PASSWORD'] = '1234App'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'

sim_config = json.load(Path("config_files_simulated/simulation-config.json").open())
sim_feeder = sim_config['power_system_config']['Line_name']
print(f"Simulation for feeder: {sim_feeder}")
gapps = GridAPPSD()
sim = Simulation(gapps, run_config=sim_config)
print("Starting Simulation")
sim.start_simulation()
assert sim.simulation_id
print(f"Simulation id is {sim.simulation_id}")
Path("simulation.feeder.txt").write_text(sim_feeder)
Path("simulation.id.txt").write_text(sim.simulation_id)
try:
    sim.run_loop()
except KeyboardInterrupt:
    print("Stopping simulation")
    sim.stop()

gapps.disconnect()
