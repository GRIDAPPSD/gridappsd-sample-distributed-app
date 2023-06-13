import importlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict

import gridappsd.field_interface.agents.agents as agents_mod
import gridappsd.topics as t
from cimlab.data_profile import CIM_PROFILE
from gridappsd.field_interface.agents import (CoordinatingAgent, FeederAgent,
                                              SecondaryAreaAgent,
                                              SwitchAreaAgent)
from gridappsd.field_interface.context import LocalContext
from gridappsd.field_interface.interfaces import MessageBusDefinition

import auth_context
import sample_queries as example

cim_profile = CIM_PROFILE.RC4_2021.value

agents_mod.set_cim_profile(cim_profile)

cim = agents_mod.cim

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('goss').setLevel(logging.ERROR)
logging.getLogger('stomp.py').setLevel(logging.ERROR)

_log = logging.getLogger(__name__)


class SampleCoordinatingAgent(CoordinatingAgent):

    def __init__(self, system_message_bus_def, simulation_id=None):
        super().__init__(None, system_message_bus_def, simulation_id)


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

        message_bus.send(reply_to, 'this is a reponse')


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
        
    def on_upstream_message(self, headers: Dict, message) -> None:
        _log.info(f"Received message from upstream message bus: {message}")

    def on_downstream_message(self, headers: Dict, message) -> None:
        _log.info(f"Received message from downstream message bus: {message}")


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

    def on_upstream_message(self, headers: Dict, message) -> None:
        _log.info(f"Received message from upstream message bus: {message}")

    def on_downstream_message(self, headers: Dict, message) -> None:
        _log.info(f"Received message from downstream message bus: {message}")

def _main():

    agent_config = {
        "app_id": "sample_app",
        "description":
        "This is a GridAPPS-D sample distribution application agent"
    }

    simulation_id_path = Path("simulation.id.txt")
    if not simulation_id_path.exists():
        print(
            "Simulation id not written, please execute `python run_simulation.py` before executing this script."
        )
        sys.exit(0)

    simulation_id = simulation_id_path.read_text().strip()

    system_message_bus_def = MessageBusDefinition.load("config_files_simulated/system-message-bus.yml")

    #TODO: add dictionary of other message bus definitions or have a functions call
    coordinating_agent = SampleCoordinatingAgent(system_message_bus_def)

    # Create feeder level distributed agent
    feeder_message_bus_def = MessageBusDefinition.load("config_files_simulated/feeder-message-bus.yml")

    #TODO: create access control for agents for different layers
    feeder_agent = SampleFeederAgent(system_message_bus_def,
                                     feeder_message_bus_def, agent_config,
                                     None, simulation_id)
    coordinating_agent.spawn_distributed_agent(feeder_agent)

    # Get all the attributes of the equipments in the feder area from the model
    #TODO: Uncomment when feeder attributed query working in gridappsd
    #print(feeder_agent.feeder_area.get_all_attributes(cim.PowerTransformer))

    # create switch area distributed agents
    switch_areas = feeder_agent.agent_area_dict['switch_areas']
    for sw_index, switch_area in enumerate(switch_areas):
        switch_area_message_bus_def = MessageBusDefinition.load(
            f"config_files_simulated/switch_area_message_bus_{sw_index}.yml")
        print("Creating switch area agent " +
              str(switch_area['message_bus_id']))
        switch_area_agent = SampleSwitchAreaAgent(feeder_message_bus_def,
                                                  switch_area_message_bus_def,
                                                  agent_config, switch_area,
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

        # Example 5 - Get TransformerTank impedances
        example.get_tank_impedances(switch_area_agent.switch_area)

        # Example 6 - Get inverter buses and phases
        example.get_inverter_buses(switch_area_agent.switch_area)

        # Example 7 - Get load buses and phases
        example.get_load_buses(switch_area_agent.switch_area)

        service_agent_id = None
        response = LocalContext.get_agents(
            switch_area_agent.downstream_message_bus)
        _log.info(f"Agents: {response}")
        for agent_id, agent_details in response.items():
            if agent_details['app_id'] == 'local_service':
                service_agent_id = agent_id

        request_queue = t.field_agent_request_queue(
            switch_area_agent.downstream_message_bus.id, service_agent_id)
        _log.debug(request_queue)
        response = switch_area_agent.downstream_message_bus.get_response(
            request_queue, {'test': 'test request'})
        _log.info(f'Response from service agent: {response}')
        
        
        message =  {
                  "timestamp": 1648512552,
                  "datatype": "test1",
                  "any_common_key": "any_value",
                  "message": [{
                      "data_timestamp": 1668109752,
                      "any_key1": 1, 
                      "any_key2": "any_value2"
                      },
                    {
                      "data_timestamp": 1648512642,
                      "any_key1": 1, 
                      "any_key2": "any_value2"
                    }
                  ],
                  "tags":["data_timestamp","any_common_key"]
                 }
        
        
        #Publishing on feeder message bus. This is subscribed by the feeder agent and agents in all switch areas.
        switch_area_agent.publish_upstream(message)
        
        #Publishing on switch message bus. This is subscribed by all secondary area agents under this switch area.
        switch_area_agent.publish_downstream(message)
        
        
        # create secondary area distributed agents
        for sec_index, secondary_area in enumerate(
                switch_area['secondary_areas']):
            secondary_area_message_bus_def = MessageBusDefinition.load(
                f"config_files_simulated/secondary_area_message_bus_{sw_index}_{sec_index}.yml")
            print("Creating secondary area agent " +
                  str(secondary_area['message_bus_id']))
            secondary_area_agent = SampleSecondaryAreaAgent(
                switch_area_message_bus_def, secondary_area_message_bus_def,
                agent_config, secondary_area, simulation_id)
            if len(secondary_area_agent.secondary_area.addressable_equipment
                   ) > 1:
                coordinating_agent.spawn_distributed_agent(
                    secondary_area_agent)

                # Example 6 - Get inverter buses and phases
                example.get_inverter_buses(secondary_area_agent.secondary_area)

                # Example 7 - Get load buses and phases
                example.get_load_buses(secondary_area_agent.secondary_area)
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
