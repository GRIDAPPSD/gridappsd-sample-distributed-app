import gridappsd.field_interface.agents.agents as agents_mod
from cimlab.data_profile import CIM_PROFILE
cim_profile = CIM_PROFILE.RC4_2021.value
agents_mod.set_cim_profile(cim_profile)
cim = agents_mod.cim

# print line name, phase, and bus
def get_lines_buses(network_area):
    print('\n \n EXAMPLE 1: GET ALL LINE PHASES AND BUSES')
    network_area.get_all_attributes(cim.ACLineSegment)
    network_area.get_all_attributes(cim.ACLineSegmentPhase)
    network_area.get_all_attributes(cim.Terminal)
    if cim.ACLineSegment in network_area.typed_catalog:
        line_ids = list(network_area.typed_catalog[cim.ACLineSegment].keys())
        for line_id in line_ids:
            line = network_area.typed_catalog[cim.ACLineSegment][line_id]
            print('line mrid: ',line_id)
            print('line name:', line.name)
            print('bus 1: ', line.Terminals[0].ConnectivityNode.name, line.Terminals[0].ConnectivityNode.mRID)
            print('bus 2: ', line.Terminals[1].ConnectivityNode.name, line.Terminals[1].ConnectivityNode.mRID)
            for line_phs in line.ACLineSegmentPhases:
                print('phase ', line_phs.phase, ': ', line_phs.mRID)
    else:
        print('no ACLineSegment objects in area')

# get line impedances and conductor geometry:

def get_line_impedances(network_area):
    print('\n \n EXAMPLE 2: GET ALL LINE IMPEDANCE ATTRIBUTES')
    network_area.get_all_attributes(cim.ACLineSegment)
    network_area.get_all_attributes(cim.ACLineSegmentPhase)
    network_area.get_all_attributes(cim.PerLengthPhaseImpedance)
    network_area.get_all_attributes(cim.PhaseImpedanceData)

    network_area.get_all_attributes(cim.WireSpacingInfo)
    network_area.get_all_attributes(cim.WirePosition)
    network_area.get_all_attributes(cim.OverheadWireInfo)
    network_area.get_all_attributes(cim.ConcentricNeutralCableInfo)
    network_area.get_all_attributes(cim.TapeShieldCableInfo)
    network_area.get_all_attributes(cim.Terminal)

# sort data by line phase
def sort_impedance_by_line(network_area):
    print('\n \n EXAMPLE 3: SORT IMPEDANCE BY LINE PHASE')
    if cim.ACLineSegment in network_area.typed_catalog:
        for line in network_area.typed_catalog[cim.ACLineSegment].values():
            print()
            print('line mrid: ', line.mRID)
            print('line name:', line.name)
            print('bus 1: ', line.Terminals[0].ConnectivityNode.mRID)
            print('bus 2: ', line.Terminals[1].ConnectivityNode.mRID)

            for line_phs in line.ACLineSegmentPhases:
                print('phase ', line_phs.phase, ': ', line_phs.mRID)
                if line_phs.WireInfo is not None:
                    print('type: ', line_phs.WireInfo.__class__.__name__)
                    print('gmr: ', line_phs.WireInfo.gmr)
                    print('insulated: ', line_phs.WireInfo.insulated)

            if line.WireSpacingInfo is not None:
                for position in line.WireSpacingInfo.WirePositions:
                    print('seq:', position.sequenceNumber, ' x:', position.xCoord, ' y:', position.yCoord)    

            if line.PerLengthImpedance is not None:
                for data in line.PerLengthImpedance.PhaseImpedanceData:
                    print('row:', data.row, 'col:', data.column, 'r:', data.r, 'x:', data.x, 'b:', data.b)
    else:
        print('info: no ACLineSegment objects in area')


# sort lines by impedance info
def sort_line_by_impedance(network_area):
    print('EXAMPLE 4: SORT LINES BY IMPEDANCE AND GEOMETRY')
    #OverheadWireInfo
    if cim.OverheadWireInfo in network_area.typed_catalog:
        for oh_wire in network_area.typed_catalog[cim.OverheadWireInfo].values():
            print()
            print('name: ', oh_wire.name)
            print('gmr: ', oh_wire.gmr)
            print('insulated:', oh_wire.insulated)
            for line_phs in oh_wire.ACLineSegmentPhases:
                node1 = line_phs.ACLineSegment.Terminals[0].ConnectivityNode
                node2 = line_phs.ACLineSegment.Terminals[1].ConnectivityNode
                print('Buses:', node1.name, node2.name)
                print('Line Phase: ', line_phs.name, line_phs.mRID)
    else:
        print('info: no OverheadWireInfo objects in area')

    #TapeShieldCableInfo
    if cim.TapeShieldCableInfo in network_area.typed_catalog:
        for cable in network_area.typed_catalog[cim.TapeShieldCableInfo].values():
            print()
            print('name: ', cable.name)
            print('gmr: ', cable.gmr)
            print('insulated:', cable.insulated)
            print('tape thickness', cable.tapeThickness)
            for line_phs in cable.ACLineSegmentPhases:
                node1 = line_phs.ACLineSegment.Terminals[0].ConnectivityNode
                node2 = line_phs.ACLineSegment.Terminals[1].ConnectivityNode
                print('Line Phase: ', line_phs.name, line_phs.mRID)
                print('Buses:', node1.name, node2.name, node1.mRID, node2.mRID)
    else:
        print('info: no TapeShieldCableInfo objects in area')

    #PerLengthPhaseImpedance
    if cim.PerLengthPhaseImpedance in network_area.typed_catalog:
        for impedance in network_area.typed_catalog[cim.PerLengthPhaseImpedance].values():
            print('name:', impedance.name)
            for data in impedance.PhaseImpedanceData:
                    print('row:', data.row, 'col:', data.column, 'r:', data.r, 'x:', data.x, 'b:', data.b)
            for line in impedance.ACLineSegments:
                node1 = line.Terminals[0].ConnectivityNode
                node2 = line.Terminals[1].ConnectivityNode
                print('Line: ', line.name, line.mRID)
                print('Buses:', node1.name, node2.name, node1.mRID, node2.mRID)
    else:
        print('no PerLengthPhaseImpedance objects in area')

    