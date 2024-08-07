import gridappsd.field_interface.agents.agents as agents_mod
from cimgraph.data_profile import CIM_PROFILE

cim_profile = CIM_PROFILE.RC4_2021.value
agents_mod.set_cim_profile(cim_profile, 7)
cim = agents_mod.cim


# print line name, phase, and bus
def get_lines_buses(network_area):
    print('\n \n EXAMPLE 1: GET ALL LINE PHASES AND BUSES')
    if cim.ACLineSegment in network_area.graph :
        network_area.get_all_edges(cim.ACLineSegment)
        network_area.get_all_edges(cim.ACLineSegmentPhase)
        network_area.get_all_edges(cim.Terminal)

        line_ids = list(network_area.graph [cim.ACLineSegment].keys())
        for line_id in line_ids:
            line = network_area.graph [cim.ACLineSegment][line_id]
            print('\n line mrid: ', line_id)
            print('line name:', line.name)
            print('bus 1: ', line.Terminals[0].ConnectivityNode.name,
                  line.Terminals[0].ConnectivityNode.mRID)
            print('bus 2: ', line.Terminals[1].ConnectivityNode.name,
                  line.Terminals[1].ConnectivityNode.mRID)
            for line_phs in line.ACLineSegmentPhases:
                print('phase ', line_phs.phase, ': ', line_phs.mRID)
    else:
        print('no ACLineSegment objects in area')


# get line impedances and conductor geometry:


def get_line_impedances(network_area):
    print('\n \n EXAMPLE 2: GET ALL LINE IMPEDANCE ATTRIBUTES')
    if cim.ACLineSegment in network_area.graph:
        network_area.get_all_edges(cim.ACLineSegment)
        network_area.get_all_edges(cim.ACLineSegmentPhase)
        network_area.get_all_edges(cim.PerLengthPhaseImpedance)
        network_area.get_all_edges(cim.PhaseImpedanceData)

        network_area.get_all_edges(cim.WireSpacingInfo)
        network_area.get_all_edges(cim.WirePosition)
        network_area.get_all_edges(cim.OverheadWireInfo)
        network_area.get_all_edges(cim.ConcentricNeutralCableInfo)
        network_area.get_all_edges(cim.TapeShieldCableInfo)
        network_area.get_all_edges(cim.Terminal)


# sort data by line phase
def sort_impedance_by_line(network_area):
    print('\n \n EXAMPLE 3: SORT IMPEDANCE BY LINE PHASE')
    if cim.ACLineSegment in network_area.graph:
        for line in network_area.graph[cim.ACLineSegment].values():
            if line.name is not None:
                print('\n line mrid: ', line.mRID)
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
                        print('seq:', position.sequenceNumber, ' x:',
                            position.xCoord, ' y:', position.yCoord)

                if line.PerLengthImpedance is not None:
                    for data in line.PerLengthImpedance.PhaseImpedanceData:
                        print('row:', data.row, 'col:', data.column, 'r:', data.r,
                            'x:', data.x, 'b:', data.b)
    else:
        print('info: no ACLineSegment objects in area')


# sort lines by impedance info
def sort_line_by_impedance(network_area):
    print('EXAMPLE 4: SORT LINES BY IMPEDANCE AND GEOMETRY')
    #OverheadWireInfo
    if cim.OverheadWireInfo in network_area.graph:
        for oh_wire in network_area.graph[
                cim.OverheadWireInfo].values():
            print('\n name: ', oh_wire.name)
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
    if cim.TapeShieldCableInfo in network_area.graph:
        for cable in network_area.graph[
                cim.TapeShieldCableInfo].values():
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
    if cim.PerLengthPhaseImpedance in network_area.graph:
        for impedance in network_area.graph[
                cim.PerLengthPhaseImpedance].values():
            print('\n name:', impedance.name)
            for data in impedance.PhaseImpedanceData:
                print('row:', data.row, 'col:', data.column, 'r:', data.r,
                      'x:', data.x, 'b:', data.b)
            for line in impedance.ACLineSegments:
                if line.Terminals:
                    node1 = line.Terminals[0].ConnectivityNode
                    node2 = line.Terminals[1].ConnectivityNode
                    print('Line: ', line.name, line.mRID)
                    print('Buses:', node1.name, node2.name, node1.mRID, node2.mRID)
    else:
        print('no PerLengthPhaseImpedance objects in area')


# get transformertank data
def get_tank_impedances(network_area):
    print('EXAMPLE 5: GET TRANSFORMER TANK IMPEDANCES')
    #OverheadWireInfo
    if cim.TransformerTank in network_area.graph:
        network_area.get_all_edges(cim.TransformerTank)
        network_area.get_all_edges(cim.TransformerTankEnd)
        network_area.get_all_edges(cim.TransformerTankInfo)
        network_area.get_all_edges(cim.TransformerEndInfo)
        network_area.get_all_edges(cim.ShortCircuitTest)
        network_area.get_all_edges(cim.NoLoadTest)
        network_area.get_all_edges(cim.Terminal)

        for tank in network_area.graph[cim.TransformerTank].values():
            print('\n name:', tank.name)
            for end in tank.TransformerTankEnds:
                print('end number:', end.endNumber)
                node = end.Terminal.ConnectivityNode
                print('bus: ', node.name, node.mRID)

            for end_info in tank.TransformerTankInfo.TransformerEndInfos:

                print('end number', end_info.endNumber)
                print('rated voltage:', end_info.ratedU)
                print('resistance:', end_info.r)
                for no_load_test in end_info.EnergisedEndNoLoadTests:
                    print('exciting current:', no_load_test.excitingCurrent)

                for short_circuit_test in end_info.EnergisedEndShortCircuitTests:
                    print('energisedEndStep:',
                          short_circuit_test.energisedEndStep)
                    print('groundedEndStep:',
                          short_circuit_test.groundedEndStep)
                    print('leakageImpedance:',
                          short_circuit_test.leakageImpedance)

                for short_circuit_test in end_info.GroundedEndShortCircuitTests:
                    print('energisedEndStep:',
                          short_circuit_test.energisedEndStep)
                    print('groundedEndStep:',
                          short_circuit_test.groundedEndStep)
                    print('leakageImpedance:',
                          short_circuit_test.leakageImpedance)


# sort PowerElectronicsUnits
def get_inverter_buses(network_area):
    if cim.PowerElectronicsConnection in network_area.graph:
        network_area.get_all_edges(cim.PowerElectronicsConnection)
        network_area.get_all_edges(cim.PowerElectronicsConnectionPhase)
        network_area.get_all_edges(cim.Terminal)
        network_area.get_all_edges(cim.Analog)

        print('\n \n EXAMPLE 6: GET ALL INVERTER PHASES AND BUSES')
        for pec in network_area.graph[
                cim.PowerElectronicsConnection].values():
            print('\n name: ', pec.name, pec.mRID)
            print('p = ', pec.p, 'q = ', pec.q)
            node1 = pec.Terminals[0].ConnectivityNode
            print('bus: ', node1.name, node1.mRID)
            for pec_phs in pec.PowerElectronicsConnectionPhases:
                print('phase ', pec_phs.phase, ': ', pec_phs.mRID)

            for meas in pec.Measurements:
                print('Measurement: ', meas.name, meas.mRID)
                print('type:', meas.measurementType, 'phases:', meas.phases)


#sort EnergyConsumers
def get_load_buses(network_area):
    if cim.EnergyConsumer in network_area.graph:
        network_area.get_all_edges(cim.EnergyConsumer)
        network_area.get_all_edges(cim.EnergyConsumerPhase)
        network_area.get_all_edges(cim.Terminal)
        network_area.get_all_edges(cim.Analog)

        print('\n \n EXAMPLE 7: GET ALL LOAD PHASES AND BUSES')

        for load in network_area.graph[cim.EnergyConsumer].values():
            print('name: ', load.name, load.mRID)
            print('p = ', load.p, 'q = ', load.q)
            node1 = load.Terminals[0].ConnectivityNode
            print('bus: ', node1.name, node1.mRID)

            for load_phs in load.EnergyConsumerPhase:
                print('phases: ', load_phs.phase)
                print('p = ', load_phs.p, 'q = ', load_phs.q)

            for meas in load.Measurements:
                print('Measurement: ', meas.name, meas.mRID)
                print('type:', meas.measurementType, 'phases:', meas.phases)


def get_power_transformers(network_area):
    if cim.PowerTransformer in network_area.graph:
        network_area.get_all_edges(cim.PowerTransformer)
        network_area.get_all_edges(cim.PowerTransformerInfo)
        network_area.get_all_edges(cim.PowerTransformerEnd)
        network_area.get_all_edges(cim.TransformerMeshImpedance)
        network_area.get_all_edges(cim.TransformerCoreAdmittance)
        network_area.get_all_edges(cim.Terminal)
        network_area.get_all_edges(cim.Analog)
        network_area.get_all_edges(cim.Discrete)

        for xfmr in network_area.graph[cim.PowerTransformer].values():
            print('\n name: ', xfmr.name, xfmr.mRID)
            for end in xfmr.PowerTransformerEnd:
                print('end number:', end.endNumber)
                print('bus:', end.Terminal.ConnectivityNode.name)
                print('connection:', end.connectionKind)
                print('voltage:', end.ratedU)

                for mesh_imp in end.ToMeshImpedance:
                    print('r:', mesh_imp.r)
                    print('x:', mesh_imp.x)
                if end.CoreAdmittance is not None:
                    print('g:', end.CoreAdmittance.g)
                    print('b:', end.CoreAdmittance.b)
            for meas in xfmr.Measurements:
                print('Measurement: ', meas.name, meas.mRID)
                print('type:', meas.measurementType, 'phases:', meas.phases)