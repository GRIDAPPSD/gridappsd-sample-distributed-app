import json
import os
from pathlib import Path

from gridappsd import GridAPPSD
from gridappsd.simulation import Simulation, SimulationConfig, PowerSystemConfig
from pprint import pprint
import auth_context

os.environ['GRIDAPPSD_APPLICATION_ID'] = 'dist-sample-sim'
os.environ['GRIDAPPSD_APPLICATION_STATUS'] = 'STARTED'
os.environ['GRIDAPPSD_USER'] = 'app_user'
os.environ['GRIDAPPSD_PASSWORD'] = '1234App'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'

# sim_config = json.load(Path("config_files_simulated/simulation-config.json").open())
# sim_feeder = sim_config['power_system_config']['Line_name']


feeder_mrid = "_C1C3E687-6FFD-C753-582B-632A27E28507"  # 123 bus
#feeder_mrid = "_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"  # 13 bus
# feeder_mrid = "_5B816B93-7A5F-B64C-8460-47C17D6E4B0F" # 13 bus asets
#feeder_mrid = "_4F76A5F9-271D-9EB8-5E31-AA362D86F2C3"  # 8500 node
#feeder_mrid = "_67AB291F-DCCD-31B7-B499-338206B9828F" # J1
#feeder_mrid = "_9CE150A8-8CC5-A0F9-B67E-BBD8C79D3095"  # R2 12.47 3
#feeder_mrid = "_EE71F6C9-56F0-4167-A14E-7F4C71F10EAA" #9500 node

psc = PowerSystemConfig(Line_name=feeder_mrid)

sim_conf = SimulationConfig(power_system_config = psc)
# sim_config = sim_conf.__dict__
sim_config = json.loads(json.dumps(sim_conf.asdict(), indent = 2))
# print(sim_config)
print(f"Simulation for feeder: {psc.Line_name}")
gapps = GridAPPSD()
sim = Simulation(gapps, run_config=sim_config)
print("Starting Simulation")
sim.start_simulation()
assert sim.simulation_id
print(f"Simulation id is {sim.simulation_id}")
Path("simulation.feeder.txt").write_text(psc.Line_name)
Path("simulation.id.txt").write_text(sim.simulation_id)
try:
    sim.run_loop()
except KeyboardInterrupt:
    print("Stopping simulation")
    sim.stop()

gapps.disconnect()