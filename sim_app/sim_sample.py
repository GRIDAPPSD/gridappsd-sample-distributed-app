import os

os.environ['GRIDAPPSD_USER'] = 'system'
os.environ['GRIDAPPSD_PASSWORD'] = 'manager'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'

import logging

logging.getLogger('stomp.py').setLevel(logging.ERROR)
_log = logging.getLogger(__name__)

import sys
import time
from pathlib import Path

from agents import *
from gridappsd import GridAPPSD
from gridappsd import topics as t
from gridappsd.simulation import Simulation
from sim_class import SimulationClass

def onMessage(header, message):
    with open("all_bus.json", "w") as fp:
            fp.write(json.dumps(message))


def main():
    gapps = GridAPPSD()
    assert gapps.connected

    sim_class = SimulationClass(gapps, "run-123.json")
    
    sim_output_topic = t.simulation_output_topic(sim_class.getSimulationID())
    sim_output_topic = '/topic/goss.gridappsd.field.simulation.output.' + sim_class.getSimulationID() + '.' + sim_class.getFeederID() + '.*'

    # following function allows us to subscribe the simulation output
    # Need a call back function
    gapps.subscribe(sim_output_topic, onMessage)

    system_message_bus_def = overwrite_parameters(sim_class.getFeederID())

    #TODO: add dictionary of other message bus definitions or have a functions call
    coordinating_agent = SampleCoordinatingAgent(sim_class.getFeederID(), system_message_bus_def)

    context = ContextManager.get_context_by_feeder(sim_class.getFeederID())

    # Create feeder level distributed agent
    feeder_message_bus_def = overwrite_parameters(sim_class.getFeederID())
    feeder = context['data']

    #TODO: create access control for agents for different layers
    feeder_agent = SampleFeederAgent(system_message_bus_def, feeder_message_bus_def, feeder, sim_class.getSimulationID())
    coordinating_agent.spawn_distributed_agent(feeder_agent)

    # create switch area distributed agents
    switch_areas = context['data']['switch_areas']
    with open("switch_areas.json", "w") as fp:
        fp.write(json.dumps(switch_areas))
    
    for sw_index, switch_area in enumerate(switch_areas):
        switch_area_message_bus_def = overwrite_parameters(sim_class.getFeederID(), f"{sw_index}")
        print("Creating switch area agent " + str(switch_area))
        switch_area_agent = SampleSwitchAreaAgent(feeder_message_bus_def,
                                                  switch_area_message_bus_def,
                                                  switch_area,
                                                  sim_class.getSimulationID())
        coordinating_agent.spawn_distributed_agent(switch_area_agent)
    
        # create secondary area distributed agents
        for sec_index, secondary_area in enumerate(switch_area['secondary_areas']):
            secondary_area_message_bus_def = overwrite_parameters(sim_class.getFeederID(), f"{sw_index}.{sec_index}")
            secondary_area_agent = SampleSecondaryAreaAgent(switch_area_message_bus_def,
                                                            secondary_area_message_bus_def,
                                                            secondary_area,
                                                            sim_class.getSimulationID())
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