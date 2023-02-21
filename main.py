import os
import auth_context
import time
import json
from configparser import ConfigParser
from simulation import Sim
from sample_agents import SampleCoordinatingAgent, SampleFeederAgent, SampleSwitchAreaAgent, SampleSecondaryAreaAgent

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('goss').setLevel(logging.INFO)
logging.getLogger('stomp.py').setLevel(logging.INFO)
log = logging.getLogger(__name__)

from gridappsd import GridAPPSD
import gridappsd.field_interface.agents.agents as agents_mod
from gridappsd.field_interface.agents import CoordinatingAgent, FeederAgent, SwitchAreaAgent, SecondaryAreaAgent
from gridappsd.field_interface.context import ContextManager
from gridappsd.field_interface.interfaces import MessageBusDefinition

import sample_queries as example
from cimlab.data_profile import CIM_PROFILE
cim_profile = CIM_PROFILE.RC4_2021.value
agents_mod.set_cim_profile(cim_profile)
cim = agents_mod.cim

GOSS_CONFIG = "config/pnnl.goss.gridappsd.cfg"
SIM_CONFIG = "config/ieee123.json"
BUS_CONFIG = "config/system_message_bus.yml"

def overwrite_parameters(feeder_id: str, area_id: str = '') -> MessageBusDefinition:
    """_summary_
    """
    bus_def = MessageBusDefinition.load(BUS_CONFIG)
    if area_id:
        bus_def.id = feeder_id + '.' + area_id
    else:
        bus_def.id = feeder_id

    address = os.environ.get('GRIDAPPSD_ADDRESS')
    port = os.environ.get('GRIDAPPSD_PORT')
    if not address or not port:
        raise ValueError("import auth_context or set environment up before this statement.")

    bus_def.conneciton_args['GRIDAPPSD_ADDRESS'] = f"tcp://{address}:{port}"
    bus_def.conneciton_args['GRIDAPPSD_USER'] = os.environ.get('GRIDAPPSD_USER')
    bus_def.conneciton_args['GRIDAPPSD_PASSWORD'] = os.environ.get('GRIDAPPSD_PASSWORD')
    return bus_def

def save_area(context: dict) -> None:
    """_summary_
    """
    with open(f"outputs/{context['message_bus_id']}.json", "w") as file:
        file.write(json.dumps(context))
        
def spawn_feeder_agent(context: dict, sim: Sim, coord_agent: SampleCoordinatingAgent) -> None:
    sys_message_bus = overwrite_parameters(sim.get_feeder_id())
    feeder_message_bus = overwrite_parameters(sim.get_feeder_id())
    save_area(context)
    agent = SampleFeederAgent(sys_message_bus,
                              feeder_message_bus,
                              context,
                              sim.get_simulation_id())
    coord_agent.spawn_distributed_agent(agent)
    
def spawn_secondary_agents(context: dict, sw_idx: int, sec_idx: int, sim: Sim, coord_agent: SampleCoordinatingAgent) -> None:
        switch_message_bus = overwrite_parameters(sim.get_feeder_id(), f"{sw_idx}")
        secondary_area_message_bus_def = overwrite_parameters(sim.get_feeder_id(), f"{sw_idx}.{sec_idx}")
        save_area(context)
        agent = SampleSecondaryAreaAgent(switch_message_bus,
                                         secondary_area_message_bus_def,
                                         context,
                                         sim.get_simulation_id())
        if len(agent.secondary_area.addressable_equipment) > 1:
            coord_agent.spawn_distributed_agent(agent)
            
def spawn_switch_area_agents(context: dict, idx: int, sim: Sim, coord_agent: SampleCoordinatingAgent) -> None:
    feeder_message_bus = overwrite_parameters(sim.get_feeder_id())
    save_area(context)
    switch_message_bus = overwrite_parameters(sim.get_feeder_id(), f"{idx}")
    agent = SampleSwitchAreaAgent(feeder_message_bus,
                                  switch_message_bus,
                                  context,
                                  sim.get_simulation_id())
    coord_agent.spawn_distributed_agent(agent)
    
    # Get all the attributes of the equipments in the switch area from the model 
    # EXAMPLE 1 - Get phase, bus info about ACLineSegments
    example.get_lines_buses(agent.switch_area)
    
    # # EXAMPLE 2 - Get all line impedance data
    # example.get_line_impedances(agent.switch_area)
    
    # # EXAMPLE 3 - Sort all line impedance by line phase:
    # example.sort_impedance_by_line(agent.switch_area)
    
    # # Example 4 - Sort all lines by impedance
    # example.sort_line_by_impedance(agent.switch_area)
    
    # # Example 5 - Get TransformerTank impedances
    # example.get_tank_impedances(agent.switch_area)
    
    # # Example 6 - Get inverter buses and phases
    # example.get_inverter_buses(agent.switch_area)
    
    # # Example 7 - Get load buses and phases
    # example.get_load_buses(agent.switch_area)
    
def load_json(path:str) -> dict:
    try:
        with open(path, encoding='utf-8') as file:
            return json.load(file)
    except IOError as error:
        raise error
    
def load_cfg(path:str) -> str:
    try:
        with open(path, 'r') as file:
            return file.read()
    except IOError as error:
        raise error
        
def compare_config(goss_config:str, sim_config) -> None:
    goss = load_cfg(goss_config)
    sim_feeder = load_json(sim_config)["power_system_config"]["Line_name"]
    assert sim_feeder in goss, f"file {goss_config} field.model.mrid does not match {sim_feeder}"
    
def main() -> None:
    compare_config(GOSS_CONFIG, SIM_CONFIG)
        
    gapps = GridAPPSD()
    assert gapps.connected

    sim = Sim(gapps, SIM_CONFIG)
    
    sys_message_bus = overwrite_parameters(BUS_CONFIG)

    coordinating_agent = SampleCoordinatingAgent(sim.get_feeder_id(), sys_message_bus)
    
    context = ContextManager.get_context_by_feeder(sim.get_feeder_id())
    
    feeder = context['data']
    spawn_feeder_agent(feeder, sim, coordinating_agent)
    
    for sw_idx, switch_area in enumerate(feeder['switch_areas']):
        spawn_switch_area_agents(switch_area, sw_idx, sim, coordinating_agent)
        
        for sec_index, secondary_area in enumerate(switch_area['secondary_areas']):
            spawn_secondary_agents(secondary_area, sw_idx, sec_index, sim, coordinating_agent)

    while not sim.done:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting sample")
            break
if __name__ == "__main__":
    main()