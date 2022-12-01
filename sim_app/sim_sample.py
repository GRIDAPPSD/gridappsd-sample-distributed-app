from gridappsd import GridAPPSD, topics as t
from gridappsd.simulation import Simulation
from sim_class import SimulationClass
from pathlib import Path
import time
import sys
from agents import *

import os
os.environ['GRIDAPPSD_USER'] = 'tutorial_user'
os.environ['GRIDAPPSD_PASSWORD'] = '12345!'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'

import logging
logging.getLogger('stomp.py').setLevel(logging.ERROR)
_log = logging.getLogger(__name__)

def main():
    gapps = GridAPPSD()
    assert gapps.connected

    sim_class = SimulationClass(gapps, "../config_files_simulated/simulation-config.json")

    system_message_bus_def = overwrite_parameters("../config_files_simulated/system-message-bus.yml", sim_class._feeder_mrid)

    #TODO: add dictionary of other message bus definitions or have a functions call
    coordinating_agent = SampleCoordinatingAgent(sim_class._feeder_mrid, system_message_bus_def)

    context = ContextManager.get_context_by_feeder(sim_class._feeder_mrid)

    # Create feeder level distributed agent
    feeder_message_bus_def = overwrite_parameters("../config_files_simulated/feeder-message-bus.yml", sim_class._feeder_mrid)
    feeder = context['data']

    #TODO: create access control for agents for different layers
    feeder_agent = SampleFeederAgent(system_message_bus_def, feeder_message_bus_def, feeder, sim_class._simulation.simulation_id)
    coordinating_agent.spawn_distributed_agent(feeder_agent)

    # create switch area distributed agents
    switch_areas = context['data']['switch_areas']
    for sw_index, switch_area in enumerate(switch_areas):
        switch_area_message_bus_def = overwrite_parameters(f"../config_files_simulated/switch_area_message_bus_{sw_index}.yml", sim_class._feeder_mrid)
        print("Creating switch area agent " + str(switch_area))
        switch_area_agent = SampleSwitchAreaAgent(feeder_message_bus_def,
                                                  switch_area_message_bus_def,
                                                  switch_area,
                                                  sim_class._simulation.simulation_id)
        coordinating_agent.spawn_distributed_agent(switch_area_agent)

        # create secondary area distributed agents
        for sec_index, secondary_area in enumerate(switch_area['secondary_areas']):
            secondary_area_message_bus_def = overwrite_parameters(f"../config_files_simulated/secondary_area_message_bus_{sw_index}_{sec_index}.yml", sim_class._feeder_mrid)
            secondary_area_agent = SampleSecondaryAreaAgent(switch_area_message_bus_def,
                                                            secondary_area_message_bus_def,
                                                            secondary_area,
                                                            sim_class._simulation.simulation_id)
            if len(secondary_area_agent.addressable_equipments) > 1:
                coordinating_agent.spawn_distributed_agent(secondary_area_agent)

    while not sim_class._finished:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting sample")
            break

if __name__ == "__main__":
    main()