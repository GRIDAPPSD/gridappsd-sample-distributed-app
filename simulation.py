from gridappsd.simulation import Simulation
from gridappsd import topics as t
import pandas as pd
import json

class Sim(object):
    """
        https://gridappsd-training.readthedocs.io/en/develop/api_usage/3.6-Controlling-Simulation-API.html
    """
    done = False

    def __init__(self, gapps_obj, config_path):
        """_summary_
        """
        self.gapps = gapps_obj
        self.load_config(config_path)
        self._feeder_mrid = self.config["power_system_config"]["Line_name"]
        self.simulation = Simulation(self.gapps, self.config)
        self.simulation.add_oncomplete_callback(self.onComplete)
        self.simulation.add_onmeasurement_callback(self.onMeasurment)
        self.simulation.add_onstart_callback(self.onStart)
        self.simulation.add_ontimestep_callback(self.onTimestep)
        self.simulation.start_simulation()

        # following function allows us to subscribe the simulation output
        # Need a call back function
        self.gapps.subscribe(t.simulation_output_topic(self.simulation.simulation_id), self.onMessage)

        # Attributes to publish difference measurements
        # self.diff = DifferenceBuilder(simulation_id)

    def load_config(self, path: str) -> None:
        """_summary_
        """
        try:
            with open(path, encoding='utf-8') as file:
                self.config = json.load(file)
        except IOError as error:
            raise error
        
    def get_feeder_id(self) -> str:
        """_summary_
        """
        return self.config["power_system_config"]["Line_name"]
    
    def get_simulation_id(self) -> str:
        """_summary_
        """
        return self.simulation.simulation_id
    
    def onStart(self, sim) -> None:
        """_summary_
        """
        # Use extra methods to subscribe to other topics, such as simulation logs
        print(f"The simulation has started with id : {self.simulation.simulation_id}")

    def onMeasurment(self, sim, timestamp, measurements) -> None:
        """_summary_
        """
        pass
        # tm = timestamp
        # print(f"A measurement was taken with timestamp : {timestamp}")
        # Print the switch status just once
        # switch_data = self._switch_df[self._switch_df['eqid'] == '_6C1FDA90-1F4E-4716-BC90-1CCB59A6D5A9']
        # print(switch_data)
        # for k in switch_data.index:
        #     measid = switch_data['measid'][k]
        #     status = measurements[measid]['value']
        #     (switch_data, status)
    
    def onTimestep(self, sim, timestep) -> None:
        """_summary_
        """
        pass

    def onComplete(self, sim) -> None:
        """_summary_
        """
        print("The simulation has finished")
        self.done = True

    def onMessage(self, headers, message) -> None:
        """_summary_
        """
        if type(message) == str:
            message = json.loads(message)

        if 'message' not in message:
            if message['processStatus'] == 'COMPLETE' or message['processStatus'] == 'CLOSED':
                print('End of Simulation')
                self.done = True
        else:
            pass
            # data = message["message"]["measurements"]
            
            # # Print the switch status just once
            # switch_data = self._switch_df[self._switch_df['eqid'] == '_6C1FDA90-1F4E-4716-BC90-1CCB59A6D5A9']
            # print(switch_data)
            # for k in switch_data.index:
            #     measid = switch_data['measid'][k]
            #     status = meas_data[measid]['value']
            #     print(switch_data, status)

            # for k in range(self._load_df.shape[0]):
            #     measid = self._load_df['measid'][k]
            #     pq = meas_data[measid]
            #     phi = (pq['angle']) * math.pi / 180
            #     kW = 0.001 * pq['magnitude'] * np.cos(phi)
            #     kVAR = 0.001 * pq['magnitude'] * np.sin(phi)
            #     print(kW, kVAR)

    def getSwitches(self) -> dict:
        """_summary_
        """
        message = {
            "modelId": self._feeder_mrid,
            "requestType": "QUERY_OBJECT_DICT",
            "resultFormat": "JSON",
            "objectType": "LoadBreakSwitch"
        }
        return self.gapps.get_response(t.REQUEST_POWERGRID_DATA, message, timeout=10)

    def getSwitchMeasurments(self) -> dict:
        """_summary_
        """
        message = {
            "modelId": self._feeder_mrid,
            "requestType": "QUERY_OBJECT_MEASUREMENTS",
            "resultFormat": "JSON",
            "objectType": "LoadBreakSwitch"
        }
        return self.gapps.get_response(t.REQUEST_POWERGRID_DATA, message, timeout=10)

    def getLoadMeasurments(self) -> dict:
        """_summary_
        """
        message = {
            "modelId": self._feeder_mrid,
            "requestType": "QUERY_OBJECT_MEASUREMENTS",
            "resultFormat": "JSON",
            "objectType": "ACLineSegment"
        }
        return self.gapps.get_response(t.REQUEST_POWERGRID_DATA, message, timeout=10)