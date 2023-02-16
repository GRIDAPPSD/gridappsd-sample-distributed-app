import auth_context
import time
from simulation import *
from agents import *

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

from cimlab.data_profile import CIM_PROFILE
cim_profile = CIM_PROFILE.RC4_2021.value
agents_mod.set_cim_profile(cim_profile)
cim = agents_mod.cim

SIM_CONFIG = "config/ieee123.json"
BUS_CONFIG = "config/system_message_bus.yml"

def save_switch_area(switch_area: dict, sw_idx: int) -> None:
    """_summary_
    """
    with open(f"outputs/switch_areas-{sw_idx}.json", "w") as file:
        file.write(json.dumps(switch_area))
        
def spawn_feeder_agent(context: dict, sim: Sim, coord_agent: SampleCoordinatingAgent) -> None:
    sys_message_bus = overwrite_parameters(BUS_CONFIG)
    feeder_message_bus = overwrite_parameters(BUS_CONFIG, sim.get_feeder_id())
    agent = SampleFeederAgent(sys_message_bus, feeder_message_bus , context['data'], sim.get_simulation_id())
    coord_agent.spawn_distributed_agent(agent)
    
def spawn_secondary_agents(context: dict, sw_idx: int, sec_idx: int, sim: Sim, coord_agent: SampleCoordinatingAgent) -> None:
        switch_message_bus = overwrite_parameters(BUS_CONFIG, sim.get_feeder_id(), f"{sw_idx}")
        secondary_area_message_bus_def = overwrite_parameters(BUS_CONFIG, sim.get_feeder_id(), f"{sw_idx}.{sec_idx}")
        agent = SampleSecondaryAreaAgent(switch_message_bus,
                                                        secondary_area_message_bus_def,
                                                        context,
                                                        sim.get_simulation_id())
        if len(agent.secondary_area.addressable_equipment) > 1:
            coord_agent.spawn_distributed_agent(agent)
            
def spawn_switch_area_agents(context: dict, idx: int, sim: Sim, coord_agent: SampleCoordinatingAgent) -> None:
    feeder_message_bus = overwrite_parameters(BUS_CONFIG, sim.get_feeder_id())
    save_switch_area(context, idx)
    switch_message_bus = overwrite_parameters(BUS_CONFIG, sim.get_feeder_id(), f"{idx}")
    agent = SampleSwitchAreaAgent(feeder_message_bus, 
                                    switch_message_bus, 
                                    context, 
                                    sim.get_feeder_id())
    coord_agent.spawn_distributed_agent(agent)
        

        
def main() -> None:
    gapps = GridAPPSD()
    assert gapps.connected

    sim = Sim(gapps, SIM_CONFIG)
    
    sys_message_bus = overwrite_parameters(BUS_CONFIG)

    coordinating_agent = SampleCoordinatingAgent(sim.get_feeder_id(), sys_message_bus)
    
    context = ContextManager.get_context_by_feeder(sim.get_feeder_id())
    
    spawn_feeder_agent(context, sim, coordinating_agent)
    
    for sw_idx, switch_area in enumerate(context['data']['switch_areas']):
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