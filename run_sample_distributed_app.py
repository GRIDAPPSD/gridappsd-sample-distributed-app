import auth_context
import importlib

import json
import logging
import os
import sys
import time
from typing import Dict


from cimlab.data_profile import CIM_PROFILE

from pathlib import Path

import gridappsd.field_interface.agents.agents as agents_mod
from gridappsd.field_interface.agents import CoordinatingAgent, FeederAgent, SwitchAreaAgent, SecondaryAreaAgent
from gridappsd.field_interface.context import ContextManager
from gridappsd.field_interface.interfaces import MessageBusDefinition

import sample_queries as example

cim_profile = CIM_PROFILE.RC4_2021.value

agents_mod.set_cim_profile(cim_profile)

cim = agents_mod.cim

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('goss').setLevel(logging.ERROR)
logging.getLogger('stomp.py').setLevel(logging.ERROR)

_log = logging.getLogger(__name__)

os.environ['GRIDAPPSD_APPLICATION_ID'] = 'dist-sample-app'
os.environ['GRIDAPPSD_APPLICATION_STATUS'] = 'STARTED'
os.environ['GRIDAPPSD_USER'] = 'app_user'
os.environ['GRIDAPPSD_PASSWORD'] = '1234App'
os.environ['GRIDAPPSD_ADDRESS'] = 'localhost'
os.environ['GRIDAPPSD_PORT'] = '61613'

class SampleCoordinatingAgent(CoordinatingAgent):

    def __init__(self, feeder_id, system_message_bus_def, simulation_id=None):
        super().__init__(feeder_id, system_message_bus_def, simulation_id)


class SampleFeederAgent(FeederAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 feeder_dict: Dict = None, simulation_id: str = None):
        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                feeder_dict, simulation_id)

        
    #TODO remove first four
    def on_measurement(self, headers: Dict, message) -> None:
        _log.debug(f"measurement: {self.__class__.__name__}.{headers.get('destination')}")
        with open("feeder.txt", "a") as fp:
            fp.write(json.dumps(message))
        #print(message)


class SampleSwitchAreaAgent(SwitchAreaAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 switch_area_dict: Dict = None, simulation_id: str = None):
        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                    switch_area_dict, simulation_id)

    def on_measurement(self, peer, sender, bus, topic, headers, message):
        _log.debug(f"measurement: {self.__class__.__name__}.{headers.get('destination')}")
        with open("switch_area.txt", "a") as fp:
            fp.write(json.dumps(message))
        #print(message)


class SampleSecondaryAreaAgent(SecondaryAreaAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 secondary_area_dict: Dict = None, simulation_id: str = None):
        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                       secondary_area_dict, simulation_id)

        

    def on_measurement(self, peer, sender, bus, topic, headers, message):
        _log.debug(f"measurement: {self.__class__.__name__}.{headers.get('destination')}")
        with open("secondary.txt", "a") as fp:
            fp.write(json.dumps(message))


def overwrite_parameters(yaml_path: str, feeder_id: str) -> MessageBusDefinition:
    bus_def = MessageBusDefinition.load(yaml_path)
    id_split = bus_def.id.split('.')
    if len(id_split) > 1:
        bus_def.id = feeder_id + '.' +'.'.join(id_split[1:])
    else:
        bus_def.id = feeder_id
    address = os.environ.get('GRIDAPPSD_ADDRESS')
    port = os.environ.get('GRIDAPPSD_PORT')
    if not address or not port:
        raise ValueError("import auth_context or set environment up before this statement.")

    bus_def.conneciton_args['GRIDAPPSD_ADDRESS'] = f"tcp://{address}:{port}"
    return bus_def


def _main():

    feeder_path = Path("simulation.feeder.txt")
    if not feeder_path.exists():
        print("Simulation feeder not written, please execute `python run_simulation.py` before this script.")
        sys.exit(0)
    simulation_id_path = Path("simulation.id.txt")
    if not simulation_id_path.exists():
        print("Simulation id not written, please execute `python run_simulation.py` before executing this script.")
        sys.exit(0)

    feeder_id = feeder_path.read_text().strip()
    simulation_id = simulation_id_path.read_text().strip()

    system_message_bus_def = overwrite_parameters("config_files_simulated/system-message-bus.yml", feeder_id)

    #TODO: add dictionary of other message bus definitions or have a functions call
    coordinating_agent = SampleCoordinatingAgent(feeder_id, system_message_bus_def)

    context = ContextManager.get_context_by_feeder(feeder_id)

    # Create feeder level distributed agent
    feeder_message_bus_def = overwrite_parameters("config_files_simulated/feeder-message-bus.yml", feeder_id)
    feeder = context['data']

    #TODO: create access control for agents for different layers
    feeder_agent = SampleFeederAgent(system_message_bus_def, feeder_message_bus_def, feeder, simulation_id)
    coordinating_agent.spawn_distributed_agent(feeder_agent)
    
    
    # Get all the attributes of the equipments in the feder area from the model 
    #TODO: Uncomment when feeder attributed query working in gridappsd
    #print(feeder_agent.feeder_area.get_all_attributes(cim.PowerTransformer))
    
    # create switch area distributed agents
    switch_areas = context['data']['switch_areas']
    for sw_index, switch_area in enumerate(switch_areas):
        switch_area_message_bus_def = overwrite_parameters(f"config_files_simulated/switch_area_message_bus_{sw_index}.yml", feeder_id)
        print("Creating switch area agent " + str(switch_area['message_bus_id']))
        switch_area_agent = SampleSwitchAreaAgent(feeder_message_bus_def,
                                                  switch_area_message_bus_def,
                                                  switch_area,
                                                  simulation_id)
        coordinating_agent.spawn_distributed_agent(switch_area_agent)
        
        # Get all the attributes of the equipments in the switch area from the model 
        
        # EXAMPLE 1 - Get phase, bus info about ACLineSegments
        example.get_lines_buses(switch_area_agent.switch_area)
        
        # EXAMPLE 2 - Get all line impedance data
        example.get_line_impedances(switch_area_agent.switch_area)
        
        # EXAMPLE 3 - Sort all line impedance by line phase:
        example.sort_impedance_by_line(switch_area_agent.switch_area)
        
        # Example 4 - Sort all lines by impedance
        example.sort_line_by_impedance(switch_area_agent.switch_area)

        # create secondary area distributed agents
        for sec_index, secondary_area in enumerate(switch_area['secondary_areas']):
            secondary_area_message_bus_def = overwrite_parameters(f"config_files_simulated/secondary_area_message_bus_{sw_index}_{sec_index}.yml", feeder_id)
            print("Creating secondary area agent " + str(switch_area['message_bus_id']))
            secondary_area_agent = SampleSecondaryAreaAgent(switch_area_message_bus_def,
                                                            secondary_area_message_bus_def,
                                                            secondary_area,
                                                            simulation_id)
            if len(secondary_area_agent.secondary_area.addressable_equipment) > 1:
                coordinating_agent.spawn_distributed_agent(secondary_area_agent)
                
                # Get all the attributes of the equipments in the switch area from the model 
                attributes = secondary_area_agent.secondary_area.get_all_attributes(cim.EnergyConsumerPhase)
                if attributes is not None:
                    print('Printing properties for secondary area EnergyConsumerPhase')
                    print(attributes)

    '''
    # Publish device data
    device = DeviceFieldInterface(
        secondary_area_message_bus_def.id,
        secondary_area_agent.downstream_message_bus,
        publish_topic=f"fieldbus/{secondary_area_message_bus_def.id}",
        control_topic=f"control/{secondary_area_message_bus_def.id}",
    )
    device.publish_field_bus()
    '''

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting sample")
            break


if __name__ == "__main__":
    _main()
