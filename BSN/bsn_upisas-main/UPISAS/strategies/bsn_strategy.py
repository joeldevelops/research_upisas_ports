from time import time

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import use

from UPISAS.PIDController import PIDController
from UPISAS.strategy import Strategy

use('TkAgg')  # Change the plotting backend to support Pycharm

"""
Constant Definitions
"""
FEVER_TEMPERATURE = 38.0
RISK_THRESHOLD = 25.0
LOW_BATTERY_THRESHOLD = 20.0
MAX_BATTERY_CAPACITY = 100.0
INITIAL_BATTERY_DRAIN = 1.0
START_TIME = time()
PLOT_LENGTH = 20


def update_plot(history: dict) -> None:
    """
    Clears the current plot window and pushes the new data
    Args:
        history: A dictionary containing the last history of the target frequencies

    Returns:
        None
    """
    plt.clf()
    for key, values in history.items():
        plt.plot(range(len(values)), values, label=key)
    plt.legend()
    plt.title('Target Frequencies of BSN Sensors per Adaptation')
    plt.xlabel('Execution Step')
    plt.ylabel('Target Frequency (Hz)')
    plt.pause(0.25)


def normalize_dict(data: dict) -> {float}:
    return {key: value / 100.0 for key, value in data.items()}


def sliding_window(data: dict, max_size=5) -> dict:
    """
    Not a real sliding window. Only take the last `max_size` elements of the array
    Args:
        data: Dictionary containing the sensor data
        max_size: Size of the window
    """
    data_copy = {}
    for key, values in data.items():
        data_copy[key] = values[-max_size:]
    return data_copy


def sensor_mean(data: dict, key: str, sensor_type: str) -> float:
    """
    Calculate the average of a dictionary entry
    Args:
        data: Dictionary containing the sensor data
        key: The type of data to be averaged
        sensor_type: The type of sensor to average data from

    Returns:
        The average of the sensor data belonging to type `key`
    """
    try:
        return np.mean([x[key] for x in data[sensor_type]]) if data else float('-inf')
    except KeyError as e:
        print("[ANALYZE]\tThis key does not exist: " + type(e).__name__ + ": " + str(e))
        return float('-inf')


def mean_arterial_pressure(pd: float, ps: float) -> float:
    """
    Calculate the mean arterial pressure. This is the average calculated blood pressure during a single cardiac cycle.
    Args:
        pd: diastolic pressure
        ps: systolic pressure

    Returns:
        MAP value
    """
    return pd + 0.33 * (ps - pd)


def calculate_batt_drain(data: dict, sensor_type: str, td: float) -> float:
    """
    Calculate the battery drain. This is necessary to decide which strategy to execute.
    Also used as the target for the PID controller
    Args:
        sensor_type: The type of sensor to calculate the battery drain of
        data: Dictionary containing the sensor data
        td: Time delta in seconds

    Returns:
        Battery drain in terms of percentage per second.
        Returns 0.0 if there isn't enough data.
        Return -inf if `key` does not exist in the dictionary. (During startup)
    """
    try:
        batt_values = [x['batt'] for x in data[sensor_type]]
        return (batt_values[-2] - batt_values[-1]) / td if len(batt_values) > 2 else 0.0
    except KeyError as e:
        print("[ANALYZE]\tThis key does not exist: " + type(e).__name__ + ": " + str(e))
        return float('-inf')


def calculate_drain_diff(value: float, increase: bool) -> float:
    return max(value, 1.0) if increase else min(value, 0.1)


def plot(hist: dict, freq: dict) -> None:
    """
    Update the dynamic target frequency plot
    Args:
        hist: History dictionary containing previous values
        freq: Dictionary containing the target frequencies of all sensors

    Returns:
        None
    """
    for key, value in freq.items():
        if len(hist[key]) >= PLOT_LENGTH:
            hist[key] = hist[key][1:]
        hist[key].append(value)
    update_plot(hist)


class BSNStrategy(Strategy):
    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.sensor_freq = 10

        # The PIDs proved difficult to tune.
        self.temperature_pid = PIDController(set_point=INITIAL_BATTERY_DRAIN, kp=0.5, ki=0.01, kd=0.01)
        self.abpd_pid = PIDController(set_point=INITIAL_BATTERY_DRAIN, kp=0.4, ki=0.1, kd=0.0)
        self.abps_pid = PIDController(set_point=INITIAL_BATTERY_DRAIN, kp=0.4, ki=0.1, kd=0.0)
        self.oximeter_pid = PIDController(set_point=INITIAL_BATTERY_DRAIN, kp=0.4, ki=0.0, kd=0.1)
        self.glucose_pid = PIDController(set_point=INITIAL_BATTERY_DRAIN, kp=0.4, ki=0.0, kd=0.1)
        self.ecg_pid = PIDController(set_point=INITIAL_BATTERY_DRAIN, kp=0.5, ki=0.1, kd=0.01)
        self.prev_time = time()
        self.sensor_types = ['/ecg_data',
                             '/abpd_data',
                             '/abps_data',
                             '/thermometer_data',
                             '/oximeter_data',
                             '/glucosemeter_data']

    def update_time(self, current_time: float) -> None:
        """
        Updates the previous timestamp to the current. Used by the PID controller
        Args:
            current_time: current timestamp in terms of seconds after the epoch

        Returns:
            None
        """
        self.prev_time = current_time

    def generate_batt_dict(self, data: dict, td: float) -> {float}:
        result = {}
        for sensor_type in self.sensor_types:
            result[sensor_type] = calculate_batt_drain(data, sensor_type, td)
        return result

    def generate_mean_dict(self, data: dict, key: str) -> {float}:
        result = {}
        for sensor_type in self.sensor_types:
            result[sensor_type] = sensor_mean(data, key, sensor_type)
        return result

    def pid_steps(self, risk: dict, batt_drain: dict, td: float) -> dict[str, float]:
        """
        Triggers the PID calculate for each of the polling rate controllers
        Args:
            risk: The risk factor for each sensor as given by ROS. Values need to be normalized between 0.0 and 100.0
            batt_drain: Dictionary containing the battery drain of each sensor
            td: Time delta

        Returns:
            A list of all target sensor frequencies
        """
        return {'/ecg_data': self.ecg_pid.calculate(batt_drain['/ecg_data'] + risk['/ecg_data'], td),
                '/abpd_data': self.abpd_pid.calculate(batt_drain['/abpd_data'] + risk['/abpd_data'], td),
                '/abps_data': self.abps_pid.calculate(batt_drain['/abps_data'] + risk['/abps_data'], td),
                '/thermometer_data': self.temperature_pid.calculate(batt_drain['/thermometer_data']
                                                                    + risk['/thermometer_data'], td),
                '/oximeter_data': self.oximeter_pid.calculate(batt_drain['/oximeter_data']
                                                              + risk['/oximeter_data'], td),
                '/glucosemeter_data': self.glucose_pid.calculate(batt_drain['/glucosemeter_data']
                                                                 + risk['/glucosemeter_data'], td)}

    def analyze(self):
        current_time = time()
        self.knowledge.analysis_data["td"] = current_time - self.prev_time
        self.update_time(current_time)

        data = sliding_window(self.knowledge.monitored_data)

        # Only start analyzing if the exemplar is done starting up.
        if len(data) < 6:
            return False

        batt_drain = self.generate_batt_dict(data, self.knowledge.analysis_data["td"])
        batt_dict = self.generate_mean_dict(data, 'batt')
        data_dict = self.generate_mean_dict(data, 'data')
        risk_dict = self.generate_mean_dict(data, 'risk')

        # Update the knowledge base
        self.knowledge.analysis_data["batt_data"] = batt_dict
        self.knowledge.analysis_data["battery_drain"] = batt_drain
        self.knowledge.analysis_data["general_data"] = data_dict
        self.knowledge.analysis_data["risk_data"] = risk_dict

        if (data_dict['/thermometer_data'] > FEVER_TEMPERATURE) or \
                any(risk > RISK_THRESHOLD for risk in risk_dict.values()):
            return True
        return any(batt < LOW_BATTERY_THRESHOLD for batt in batt_dict.values())

    def update_set_point(self, sensor_type: str, increase: bool) -> None:
        value = None
        if sensor_type == '/thermometer_data':
            value = self.temperature_pid.get_set_point()
            self.temperature_pid.update_set_point(calculate_drain_diff(value, increase))
        elif sensor_type == '/ecg_data':
            value = self.ecg_pid.get_set_point()
            self.ecg_pid.update_set_point(calculate_drain_diff(value, increase))
        elif sensor_type == '/oximeter_data':
            value = self.oximeter_pid.get_set_point()
            self.oximeter_pid.update_set_point(calculate_drain_diff(value, increase))
        elif sensor_type == '/abpd_data':
            value = self.abpd_pid.get_set_point()
            self.abpd_pid.update_set_point(calculate_drain_diff(value, increase))
        elif sensor_type == '/abps_data':
            value = self.abps_pid.get_set_point()
            self.abps_pid.update_set_point(calculate_drain_diff(value, increase))
        elif sensor_type == '/glucosemeter_data':
            value = self.glucose_pid.get_set_point()
            self.glucose_pid.update_set_point(calculate_drain_diff(value, increase))
        return value

    def plan(self):
        execute, risk_factor, battery_factor = False, False, False
        self.knowledge.plan_data = {}

        batt_drain = self.knowledge.analysis_data["battery_drain"]
        batt_dict = self.knowledge.analysis_data["batt_data"]
        data_dict = self.knowledge.analysis_data["general_data"]
        risk_dict = self.knowledge.analysis_data["risk_data"]

        # Update all PID controllers
        target_frequencies = self.pid_steps(normalize_dict(risk_dict), batt_drain, self.knowledge.analysis_data["td"])
        # A bit unorthodox, but I need this information in the main loop for plotting
        self.knowledge.analysis_data['target_frequencies'] = target_frequencies

        # Increase target battery drain in case of a fever
        if data_dict['/thermometer_data'] > FEVER_TEMPERATURE:
            print(self.update_set_point('/thermometer_data', increase=True))
            self.knowledge.plan_data['/thermometer_data'] = {"topic": '/thermometer_data',
                                                             "target": '/thermometer_data',
                                                             "action": "freq=" + str(target_frequencies['/thermometer_data'])}
            execute = True

        # Increase target battery drain in case of high risk
        for sensor, risk in risk_dict.items():
            if risk > RISK_THRESHOLD:
                print(self.update_set_point(sensor, increase=True))
                self.knowledge.plan_data[sensor] = {"topic": sensor,
                                                    "target": sensor,
                                                    "action": "freq=" + str(target_frequencies[sensor])}
                execute, risk_factor = True, True
            elif risk < RISK_THRESHOLD // 2:
                print(self.update_set_point(sensor, increase=False))
                self.knowledge.plan_data[sensor] = {"topic": sensor,
                                                    "target": sensor,
                                                    "action": "freq=" + str(target_frequencies[sensor])}
                execute, risk_factor = True, True

        # Decrease target battery drain in case of low battery
        for sensor, batt in batt_dict.items():
            if batt < LOW_BATTERY_THRESHOLD:
                print(self.update_set_point(sensor, increase=False))
                self.knowledge.plan_data[sensor] = {"topic": sensor,
                                                    "target": sensor,
                                                    "action": "freq=" + str(target_frequencies[sensor])}
                execute, battery_factor = True, True
            elif batt > (MAX_BATTERY_CAPACITY - (MAX_BATTERY_CAPACITY / 10.0)):
                print(self.update_set_point(sensor, increase=True))
                self.knowledge.plan_data[sensor] = {"topic": sensor,
                                                    "target": sensor,
                                                    "action": "freq=" + str(target_frequencies[sensor])}
        if execute:
            print(batt_dict)
            print(risk_dict)
            print('----------------------------------------------------')
        return execute
