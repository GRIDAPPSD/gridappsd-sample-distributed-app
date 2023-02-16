import json
import os
from typing import Dict

import gridappsd.field_interface.agents.agents as agents_mod
from gridappsd.field_interface.agents import CoordinatingAgent, FeederAgent, SwitchAreaAgent, SecondaryAreaAgent
from gridappsd.field_interface.context import ContextManager
from gridappsd.field_interface.interfaces import MessageBusDefinition

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('goss').setLevel(logging.INFO)
logging.getLogger('stomp.py').setLevel(logging.INFO)
log = logging.getLogger(__name__)

class SampleCoordinatingAgent(CoordinatingAgent):

    def __init__(self, feeder_id, system_message_bus_def, simulation_id=None):
        super().__init__(feeder_id, system_message_bus_def, simulation_id)


class SampleFeederAgent(FeederAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 feeder_dict: Dict = None, simulation_id: str = None):
        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                feeder_dict, simulation_id)
        self._latch = False

        
    #TODO remove first four
    def on_measurement(self, headers: Dict, message) -> None:
        if not self._latch:
            log.debug(f"measurement: {self.__class__.__name__}.{headers.get('destination')}")
            with open("feeder.txt", "w") as fp:
                fp.write(json.dumps(message))
            self._latch = True


class SampleSwitchAreaAgent(SwitchAreaAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 switch_area_dict: Dict = None, simulation_id: str = None):
        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                    switch_area_dict, simulation_id)
        self._latch = False

    def on_measurement(self, headers: Dict, message):
        if not self._latch:
            log.debug(f"measurement: {self.__class__.__name__}.{headers.get('destination')}")
            with open("switch_area.txt", "w") as fp:
                fp.write(json.dumps(message))
            self._latch = True
        


class SampleSecondaryAreaAgent(SecondaryAreaAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 secondary_area_dict: Dict = None, simulation_id: str = None):
        super().__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                       secondary_area_dict, simulation_id)
        self._latch = False

        

    def on_measurement(self, headers: Dict, message):
        if not self._latch:
            log.debug(f"measurement: {self.__class__.__name__}.{headers.get('destination')}")
            with open("secondary.txt", "w") as fp:
                fp.write(json.dumps(message))
            self._latch = True

def overwrite_parameters(path: str, feeder_id: str = '', area_id: str = '') -> MessageBusDefinition:
    """_summary_
    """
    bus_def = MessageBusDefinition.load(path)
    if feeder_id and area_id:
        bus_def.id = feeder_id + '.' + area_id 
    elif feeder_id and not area_id:
        bus_def.id = feeder_id
        
    print(bus_def.id)
    address = os.environ.get('GRIDAPPSD_ADDRESS')    
    port = os.environ.get('GRIDAPPSD_PORT')
    if not address or not port:
        raise ValueError("import auth_context or set environment up before this statement.")

    bus_def.conneciton_args['GRIDAPPSD_ADDRESS'] = f"tcp://{address}:{port}"
    bus_def.conneciton_args['GRIDAPPSD_USER'] = os.environ.get('GRIDAPPSD_USER')
    bus_def.conneciton_args['GRIDAPPSD_PASSWORD'] = os.environ.get('GRIDAPPSD_PASSWORD')
    return bus_def