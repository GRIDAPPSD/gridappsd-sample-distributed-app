import json
import sys
import os
from gridappsd.field_interface.agents import CoordinatingAgent, FeederAgent, SwitchAreaAgent, SecondaryAreaAgent
from gridappsd.field_interface.context import ContextManager
from gridappsd.field_interface.interfaces import MessageBusDefinition, DeviceFieldInterface

class SampleCoordinatingAgent(CoordinatingAgent):

    def __init__(self, feeder_id, system_message_bus_def, simulation_id=None):
        super(SampleCoordinatingAgent, self).__init__(feeder_id, system_message_bus_def, simulation_id)


class SampleFeederAgent(FeederAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 feeder_dict=None, simulation_id=None):
        super(SampleFeederAgent, self).__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                feeder_dict, simulation_id)
    #TODO remove first four
    def on_measurement(self, peer, sender, bus, topic, headers, message):
        with open("feeder.txt", "a") as fp:
            fp.write(json.dumps(message))
        print(message)


class SampleSwitchAreaAgent(SwitchAreaAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 switch_area_dict=None, simulation_id=None):
        super(SampleSwitchAreaAgent, self).__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                    switch_area_dict, simulation_id)

    def on_measurement(self, peer, sender, bus, topic, headers, message):
        print('Switch Area on measurment')
        with open("switch_area.txt", "a") as fp:
            fp.write(json.dumps(message))
        print(message)


class SampleSecondaryAreaAgent(SecondaryAreaAgent):

    def __init__(self, upstream_message_bus_def: MessageBusDefinition, downstream_message_bus_def: MessageBusDefinition,
                 secondary_area_dict=None, simulation_id=None):
        super(SampleSecondaryAreaAgent, self).__init__(upstream_message_bus_def, downstream_message_bus_def,
                                                       secondary_area_dict, simulation_id)

    def on_measurement(self, peer, sender, bus, topic, headers, message):
        print('Secondary Area on measurment')
        with open("secondary.txt", "a") as fp:
            if "_4c491539-dfc1-4fda-9841-3bf10348e2fa" in json.dumps(message):
                print("Woot found it!")
                sys.exit()
            fp.write(json.dumps(message))
        print(message)
        
def overwrite_parameters(yaml_path: str, feeder_id: str) -> MessageBusDefinition:
    bus_def = MessageBusDefinition.load(yaml_path)
    id_split = bus_def.id.split('.')
    if len(id_split) > 1:
        bus_def.id = feeder_id + '.'.join(id_split[1:])
    else:
        bus_def.id = feeder_id
    address = os.environ.get('GRIDAPPSD_ADDRESS')
    port = os.environ.get('GRIDAPPSD_PORT')
    if not address or not port:
        raise ValueError("import auth_context or set environment up before this statement.")

    bus_def.conneciton_args['GRIDAPPSD_ADDRESS'] = f"tcp://{address}:{port}"
    return bus_def