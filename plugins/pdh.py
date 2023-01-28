import pandas as pd
from typing import Callable, Dict, Tuple

pd.options.mode.chained_assignment = None


def defineMetrics() -> Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]:
    """Returns a list of the metrics contained in this group and their corresponding functions."""
    return {
        "Starting Voltage": ProcessStartingVoltage,
        "Ending Voltage": ProcessEndingVoltage,
    }


def ProcessStartingVoltage(robotTelemetry: pd.DataFrame) -> Tuple(int, str):
    """Process the power distribution hub pressure telemetry data.

    Uses this data to calculate the voltage the robot's battery starts at.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    voltage = robotTelemetry[robotTelemetry["Key"] == "PDH Input Voltage (V)"]
    if voltage.empty:
        return -1, "metric_not_implemented"
    voltage["PDH Input Voltage (V)"] = pd.to_numeric(voltage["Value"])

    startVoltage = voltage["PDH Input Voltage (V)"].iloc[0]
    startVoltageMetricEncoding = 0
    if startVoltage < 11.5:
        startVoltageMetricEncoding = 2
    elif startVoltage < 11.7:
        startVoltageMetricEncoding = 1

    return startVoltageMetricEncoding, str(startVoltage)


def ProcessEndingVoltage(robotTelemetry: pd.DataFrame) -> Tuple(int, str):
    """Process the power distribution hub pressure telemetry data.

    Uses this data to calculate the voltage the robot's battery ends at.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    voltage = robotTelemetry[robotTelemetry["Key"] == "PDH Input Voltage (V)"]
    if voltage.empty:
        return -1, "metric_not_implemented"
    voltage["PDH Input Voltage (V)"] = pd.to_numeric(voltage["Value"])

    endVoltage = voltage["PDH Input Voltage (V)"].iloc[-1]
    endVoltageMetricEncoding = 0
    if endVoltage < 11.0:
        endVoltageMetricEncoding = 2
    elif endVoltage < 11.2:
        endVoltageMetricEncoding = 1

    return endVoltageMetricEncoding, str(endVoltage)
