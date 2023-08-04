import importlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict

import gridappsd.field_interface.agents.agents as agents_mod
from cimgraph.data_profile import CIM_PROFILE
from gridappsd.field_interface.agents import (CoordinatingAgent, FeederAgent,
                                              SecondaryAreaAgent,
                                              SwitchAreaAgent)
from gridappsd.field_interface.context import LocalContext
from gridappsd.field_interface.interfaces import MessageBusDefinition

import auth_context

cim_profile = CIM_PROFILE.RC4_2021.value

agents_mod.set_cim_profile(cim_profile)

cim = agents_mod.cim

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('goss').setLevel(logging.ERROR)
logging.getLogger('stomp.py').setLevel(logging.ERROR)

_log = logging.getLogger(__name__)


class SampleCoordinatingAgent(CoordinatingAgent):

    def __init__(self, feeder_id, system_message_bus_def, simulation_id=None):
        super().__init__(feeder_id, system_message_bus_def, simulation_id)


class SampleFeederAgent(FeederAgent):

    def __init__(self,
                 upstream_message_bus_def: MessageBusDefinition,
                 downstream_message_bus_def: MessageBusDefinition,
                 agent_config,
                 feeder_dict: Dict = None,
                 simulation_id: str = None):

        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                         agent_config, feeder_dict, simulation_id)

    #TODO remove first four
    def on_measurement(self, headers: Dict, message) -> None:
        _log.debug(
            f"measurement: {self.__class__.__name__}.{headers.get('destination')}"
        )
        with open("feeder.txt", "a") as fp:
            fp.write(json.dumps(message))
        #print(message)

    def on_upstream_message(self, headers: Dict, message) -> None:
        print(f"Received message from upstream message bus: {message}")

    def on_downstream_message(self, headers: Dict, message) -> None:
        print(f"Received message from downstream message bus: {message}")

    def on_request(self, message_bus, headers: Dict, message):
        print(f"Received request: {message}")

        reply_to = headers['reply-to']

        message_bus.send(reply_to,
                         {'test_response': 'this is a test response'})


class SampleSwitchAreaAgent(SwitchAreaAgent):

    def __init__(self,
                 upstream_message_bus_def: MessageBusDefinition,
                 downstream_message_bus_def: MessageBusDefinition,
                 agent_config,
                 switch_area_dict: Dict = None,
                 simulation_id: str = None):

        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                         agent_config, switch_area_dict, simulation_id)

    def on_measurement(self, headers: Dict, message):
        _log.debug(
            f"measurement: {self.__class__.__name__}.{headers.get('destination')}"
        )
        with open("switch_area.txt", "a") as fp:
            fp.write(json.dumps(message))
        #print(message)

    def on_request(self, message_bus, headers: Dict, message):
        print(f"Received request: {message}")

        reply_to = headers['reply-to']

        message_bus.send(reply_to,
                         {'test_response': 'this is a test response'})


class SampleSecondaryAreaAgent(SecondaryAreaAgent):

    def __init__(self,
                 upstream_message_bus_def: MessageBusDefinition,
                 downstream_message_bus_def: MessageBusDefinition,
                 agent_config,
                 secondary_area_dict: Dict = None,
                 simulation_id: str = None):

        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                         agent_config, secondary_area_dict, simulation_id)

    def on_measurement(self, headers: Dict, message):
        _log.debug(
            f"measurement: {self.__class__.__name__}.{headers.get('destination')}"
        )
        with open("secondary.txt", "a") as fp:
            fp.write(json.dumps(message))

    def on_request(self, message_bus, headers: Dict, message):
        print(f"Received request: {message}")

        reply_to = headers['reply-to']

        message_bus.send(reply_to,
                         {'test_response': 'this is a test response'})


def overwrite_parameters(yaml_path: str,
                         feeder_id: str) -> MessageBusDefinition:
    bus_def = MessageBusDefinition.load(yaml_path)
    id_split = bus_def.id.split('.')
    if len(id_split) > 1:
        bus_def.id = feeder_id + '.' + '.'.join(id_split[1:])
    else:
        bus_def.id = feeder_id
    address = os.environ.get('GRIDAPPSD_ADDRESS')
    port = os.environ.get('GRIDAPPSD_PORT')
    if not address or not port:
        raise ValueError(
            "import auth_context or set environment up before this statement.")

    bus_def.conneciton_args['GRIDAPPSD_ADDRESS'] = f"tcp://{address}:{port}"
    return bus_def


def _main():

    agent_config = {
        "app_id": "local_service",
        "description": "This is a GridAPPS-D sample distributed service agent"
    }

    feeder_path = Path("simulation.feeder.txt")
    if not feeder_path.exists():
        print(
            "Simulation feeder not written, please execute `python run_simulation.py` before this script."
        )
        sys.exit(0)
    simulation_id_path = Path("simulation.id.txt")
    if not simulation_id_path.exists():
        print(
            "Simulation id not written, please execute `python run_simulation.py` before executing this script."
        )
        sys.exit(0)

    feeder_id = feeder_path.read_text().strip()
    simulation_id = simulation_id_path.read_text().strip()

    system_message_bus_def = overwrite_parameters(
        "config_files_simulated/system-message-bus.yml", feeder_id)

    #TODO: add dictionary of other message bus definitions or have a functions call
    coordinating_agent = SampleCoordinatingAgent(feeder_id,
                                                 system_message_bus_def)

    context = LocalContext.get_context_by_feeder(
        coordinating_agent.downstream_message_bus, feeder_id)

    # Create feeder level distributed agent
    feeder_message_bus_def = overwrite_parameters(
        "config_files_simulated/feeder-message-bus.yml", feeder_id)
    feeder = context['data']

    #TODO: create access control for agents for different layers
    feeder_agent = SampleFeederAgent(system_message_bus_def,
                                     feeder_message_bus_def, agent_config,
                                     feeder, simulation_id)
    
    # create switch area distributed agents
    switch_areas = context['data']['switch_areas']
    for sw_index, switch_area in enumerate(switch_areas):
        switch_area_message_bus_def = overwrite_parameters(
            f"config_files_simulated/switch_area_message_bus_{sw_index}.yml",
            feeder_id)
        print("Creating switch area agent " +
              str(switch_area['message_bus_id']))
        switch_area_agent = SampleSwitchAreaAgent(feeder_message_bus_def,
                                                  switch_area_message_bus_def,
                                                  agent_config, switch_area,
                                                  simulation_id)
        
        # create secondary area distributed agents
        for sec_index, secondary_area in enumerate(
                switch_area['secondary_areas']):
            secondary_area_message_bus_def = overwrite_parameters(
                f"config_files_simulated/secondary_area_message_bus_{sw_index}_{sec_index}.yml",
                feeder_id)
            print("Creating secondary area agent " +
                  str(secondary_area['message_bus_id']))
            secondary_area_agent = SampleSecondaryAreaAgent(
                switch_area_message_bus_def, secondary_area_message_bus_def,
                agent_config, secondary_area, simulation_id)
            if len(secondary_area_agent.secondary_area.addressable_equipment) == 0:
                _log.info(f"No addressable equipment in the area {secondary_area_agent.downstream_message_bus.id}. Disconnecting the agent.")
                secondary_area_agent.disconnect()
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
