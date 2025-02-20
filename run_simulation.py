import json
import os
from datetime import datetime, timezone
from pathlib import Path

from gridappsd import GridAPPSD
from gridappsd.simulation import Simulation, SimulationArgs, SimulationConfig, PowerSystemConfig
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
#feeder_mrid = "C1C3E687-6FFD-C753-582B-632A27E28507"  # 123 bus
feeder_mrid = "49AD8E07-3BF9-A4E2-CB8F-C3722F837B62"  # 13 bus
# feeder_mrid = "5B816B93-7A5F-B64C-8460-47C17D6E4B0F" # 13 bus asets
#feeder_mrid = "9CE150A8-8CC5-A0F9-B67E-BBD8C79D3095"  # R2 12.47 3
#feeder_mrid = "EE71F6C9-56F0-4167-A14E-7F4C71F10EAA" #9500 node
gapps = GridAPPSD()
response = gapps.query_model_info()
models = response.get("data", {}).get("models", [])
model = None
for m in models:
    if m.get("modelId") == feeder_mrid:
        model = m
psc = PowerSystemConfig(Line_name=model.get("modelId"),
                        SubGeographicalRegion_name=model.get("subRegionId"),
                        GeographicalRegion_name=model.get("regionId"))
sim_args = SimulationArgs(
    start_time=int(datetime(2025, 1, 1, 0, tzinfo=timezone.utc).timestamp()),
    duration=300,
    run_realtime=True,
    pause_after_measurements=False
)
sim_config = SimulationConfig(power_system_config=psc, simulation_config=sim_args)
# print(sim_config)
print(f"Simulation for feeder: {psc.Line_name}")
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
