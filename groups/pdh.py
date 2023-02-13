import pandas as pd
import numpy as np
from typing import Callable, Dict, Tuple

pd.options.mode.chained_assignment = None
# PDP ID: (name, (yellow max, red max), (yellow average, red average))
channelMapping: Dict[int, Tuple[str, Tuple[float, float], Tuple[float, float]]] = {
    13: ("Front Left Turn Motor", (40, 60), (5, 20)),
    2: ("Front Right Turn Motor", (40, 60), (5, 20)),
    14: ("Rear Left Turn Motor", (40, 60), (5, 20)),
    1: ("Rear Right Turn Motor", (40, 60), (5, 20)),
    12: ("Front Left Drive Motor", (40, 60), (20, 40)),
    3: ("Front Right Drive Motor", (40, 60), (20, 40)),
    15: ("Rear Left Drive Motor", (40, 60), (20, 40)),
    20: ("Rear Right Drive Motor", (40, 60), (20, 40)),
}


def GenerateMotorCurrentMetrics() -> Dict[
    str, Callable[[pd.DataFrame], Tuple[int, str]]
]:
    result = {}
    for key in channelMapping.keys():
        result[f"{channelMapping[key][0]} Max Current"] = lambda df: ProcessMaxCurrent(
            key, df
        )
        result[
            f"{channelMapping[key][0]} Average Current"
        ] = lambda df: ProcessAverageCurrent(key, df)
    return result


def defineMetrics() -> Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]:
    """Returns a list of the metrics contained in this group and their corresponding functions."""
    regularDict = {
        "Starting Voltage": ProcessStartingVoltage,
        "Ending Voltage": ProcessEndingVoltage,
        "Max Current Draw": ProcessMaxCurrentDraw,
        "Max PDH Temperature": ProcessMaxPDHTemperature,
    }
    return regularDict | GenerateMotorCurrentMetrics()


def ProcessStartingVoltage(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the power distribution hub voltage data.

    Uses this data to calculate the voltage the robot's battery starts at.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    voltage = robotTelemetry[robotTelemetry["Key"] == "/pdh/voltage"]
    if voltage.empty:
        return -1, "metric_not_implemented"
    voltage["PDH Input Voltage (V)"] = pd.to_numeric(voltage["Value"])

    startVoltage = voltage["PDH Input Voltage (V)"].iloc[0]
    startVoltageMetricEncoding = 0
    if startVoltage < 12.0:
        startVoltageMetricEncoding = 2
    elif startVoltage < 12.15:
        startVoltageMetricEncoding = 1

    return startVoltageMetricEncoding, f"{startVoltage} V"


def ProcessEndingVoltage(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the power distribution hub pressure voltage data.

    Uses this data to calculate the voltage the robot's battery ends at.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    voltage = robotTelemetry[robotTelemetry["Key"] == "/pdh/voltage"]
    if voltage.empty:
        return -1, "metric_not_implemented"
    voltage["PDH Input Voltage (V)"] = pd.to_numeric(voltage["Value"])

    endVoltage = voltage["PDH Input Voltage (V)"].iloc[-1]
    endVoltageMetricEncoding = 0
    if endVoltage < 11.0:
        endVoltageMetricEncoding = 2
    elif endVoltage < 11.2:
        endVoltageMetricEncoding = 1

    return endVoltageMetricEncoding, f"{endVoltage} V"


def ProcessMaxCurrentDraw(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the power distribution hub channel currents data.

    Uses this data to calculate the most current that the robot drew.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    currents = robotTelemetry[robotTelemetry["Key"] == "/pdh/currents"]
    if currents.empty:
        return -1, "metric_not_implemented"
    totalCurrents = currents["Value"].to_numpy()
    # Turn the array of arrays into a 2d array
    totalCurrents = np.stack(totalCurrents)
    # Sum up the per channel current draws into one total value
    totalCurrents = totalCurrents.sum(axis=1)
    # Get the highest value
    maxCurrent = totalCurrents.max()
    stoplight = 0
    if maxCurrent > 120:
        stoplight = 2
    elif maxCurrent > (120 * 0.8) and stoplight != 2:
        stoplight = 1
    return stoplight, f"{maxCurrent} A"


def ProcessMaxPDHTemperature(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the power distribution hub temperature data.

    Uses this data to calculate whether or not the PDH reaches concerning temperatures.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    temperature = robotTelemetry[robotTelemetry["Key"] == "/pdh/temperature"]
    if temperature.empty:
        return -1, "metric_not_implemented"
    temperature["PDH Temperature (°C)"] = pd.to_numeric(temperature["Value"])

    maxTemp = temperature["PDH Temperature (°C)"].max()
    maxTempMetricEncoding = 0
    if maxTemp > 50:
        maxTempMetricEncoding = 2
    elif maxTemp > 40 and maxTempMetricEncoding != 2:
        maxTempMetricEncoding = 1

    return maxTempMetricEncoding, f"{maxTemp} °C"


def ProcessMaxCurrent(pdpId: int, robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the maximum current draw of a PDH port given its ID and uses it to determine a severity.

    Args:
        pdpId: The PDP channel ID to check
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    currents = robotTelemetry[robotTelemetry["Key"] == "/pdh/currents"]
    if currents.empty:
        return -1, "metric_not_implemented"
    totalCurrents = currents["Value"].to_numpy()
    # Turn the array of arrays into a 2d array
    totalCurrents = np.stack(totalCurrents)
    # Get the currents for one port
    portCurrrent = totalCurrents[:, pdpId]
    # Find the maximum
    maxCurrent = portCurrrent.max()
    stoplight = 0
    if maxCurrent > channelMapping[pdpId][1][1]:
        stoplight = 2
    elif maxCurrent > channelMapping[pdpId][1][0] and stoplight != 2:
        stoplight = 1
    return stoplight, f"{maxCurrent} A"


def ProcessAverageCurrent(pdpId: int, robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the average current draw of a PDH port given its ID and uses it to determine a severity.

    Args:
        pdpId: The PDP channel ID to check
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    currents = robotTelemetry[robotTelemetry["Key"] == "/pdh/currents"]
    if currents.empty:
        return -1, "metric_not_implemented"
    totalCurrents = currents["Value"].to_numpy()
    # Turn the array of arrays into a 2d array
    totalCurrents = np.stack(totalCurrents)
    # Get the currents for one port
    portCurrrent = totalCurrents[:, pdpId]
    # Find the mean
    maxCurrent = portCurrrent.mean()
    stoplight = 0
    if maxCurrent > channelMapping[pdpId][2][1]:
        stoplight = 2
    elif maxCurrent > channelMapping[pdpId][2][0] and stoplight != 2:
        stoplight = 1
    return stoplight, f"{maxCurrent} A"
