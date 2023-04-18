import pandas as pd
import numpy as np
from typing import Callable, Dict, Tuple

pd.options.mode.chained_assignment = None

def defineMetrics() -> Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]:
    """Returns a list of the metrics contained in this group and their corresponding functions."""
    return {
        "Max Manipulator Current": ProcessMaxCurrent,
        "Avg Manipulator Current": ProcessAverageCurrent,
        "Max Manipulator Temperature": ProcessMaxMotorTemp,
        "Avg Manipulator Temperature": ProcessAvgMotorTemp
    }

def ProcessMaxCurrent(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the maximum current draw of the manipulator's motor and uses it to determine a severity.

    Args:
        motorKey: The motor key to check
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    currents = robotTelemetry[robotTelemetry["Key"] == "/manipulator/motor/current"]
    if currents.empty:
        return -1, "metric_not_implemented"
    currents["Value"] = pd.to_numeric(currents["Value"])
    # Find the mean
    maxCurrent = (np.convolve(currents["Value"].to_numpy(), np.ones(50), "valid") / 50).max()
    stoplight = 0
    if maxCurrent > 50:
        stoplight = 2
    elif maxCurrent > 45 and stoplight != 2:
        stoplight = 1
    return stoplight, f"{maxCurrent} A"


def ProcessAverageCurrent(
        robotTelemetry: pd.DataFrame
) -> Tuple[int, str]:
    """Process the average current draw of the manipulator's motor and uses it to determine a severity.

    Args:
        motorKey: The motor key to check
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    currents = robotTelemetry[robotTelemetry["Key"] == f"/manipulator/motor/current"]
    if currents.empty:
        return -1, "metric_not_implemented"
    outputs = robotTelemetry[robotTelemetry["Key"] == f"/manipulator/motor/output"]
    if outputs.empty:
        return -1, "metric_not_implemented"
    currents = pd.to_numeric(currents["Value"])
    outputs = pd.to_numeric(outputs["Value"])
    # Create dataframe
    df = pd.DataFrame({"Out": outputs, "Current": currents})
    # Interpolate
    df = df.interpolate(limit_process="both")
    # Find the mean
    avgCurrent = df["Current"].mean()
    stoplight = 0
    if avgCurrent > 40:
        stoplight = 2
    elif avgCurrent > 35 and stoplight != 2:
        stoplight = 1
    return stoplight, f"{avgCurrent} A"

def ProcessMaxMotorTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Checks the temperature of the manipulator's motor.
    Args:
        moduleKey: The key of the motor to check alignment for
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.
    Raises:
        None
    """
    # Grab data
    values = robotTelemetry[robotTelemetry["Key"] == f"/elevator/motor/temp"]
    if values.empty:
        return -1, "metric_not_implemented"
    # Cut out the garbage data at the beginning
    values = values.iloc[10:]
    # Convert to Numpy array
    valuesNp = pd.to_numeric(values["Value"]).to_numpy()
    maxTemp = valuesNp.max()
    stoplight = 0
    if maxTemp > 50:
        stoplight = 2
    elif maxTemp > 40 and stoplight == 0:
        stoplight = 1
    return stoplight, f"{maxTemp} °C"

def ProcessAvgMotorTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Checks the temperature of the manipulator's motor
    Args:
        moduleKey: The key of the motor to check alignment for
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.
    Raises:
        None
    """
    # Grab data
    values = robotTelemetry[robotTelemetry["Key"] == f"/elevator/motor/temp"]
    if values.empty:
        return -1, "metric_not_implemented"
    # Cut out the garbage data at the beginning
    values = values.iloc[10:]
    # Convert to Numpy array
    valuesNp = pd.to_numeric(values["Value"]).to_numpy()
    avgTemp = valuesNp.mean()
    stoplight = 0
    if avgTemp > 40:
        stoplight = 2
    elif avgTemp > 35 and stoplight == 0:
        stoplight = 1
    return stoplight, f"{avgTemp} °C"