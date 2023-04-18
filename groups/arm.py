import pandas as pd
import numpy as np
from typing import Callable, Dict, Tuple

pd.options.mode.chained_assignment = None

def defineMetrics() -> Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]:
    """Returns a list of the metrics contained in this group and their corresponding functions."""
    return {
        "Avg Arm Error": ProcessAverageArmError,
        "Max Arm Current": ProcessMaxCurrent,
        "Avg Arm Current": ProcessAverageCurrent,
        "Max Arm Temperature": ProcessMaxMotorTemp,
        "Avg Arm Temperature": ProcessAvgMotorTemp
    }

def ProcessAverageArmError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Checks the mean error of the arm's motor.
    Args:
        processKey: The key of the process variable to test
        setpointKey: The key of the setpoint the process variable is trying to track
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.
    Raises:
        None
    """
    # Grab data
    process = robotTelemetry[robotTelemetry["Key"] == "/arm/absolute/velocity"]
    if process.empty:
        return -1, "metric_not_implemented"
    setpoint = robotTelemetry[robotTelemetry["Key"] == "/arm/setpoint/velocity"]
    if setpoint.empty:
        return -1, "metric_not_implemented"
    fmsMode = robotTelemetry[robotTelemetry["Key"] == "DS:enabled"]
    if fmsMode.empty:
        return -1, "metric_not_implemented"
    # Cut out the garbage data at the beginning
    process = process.iloc[10:]
    setpoint = setpoint.iloc[10:]
    # Convert to numeric
    process["Value"] = pd.to_numeric(process["Value"])
    setpoint["Value"] = pd.to_numeric(setpoint["Value"])
    # Only get data when robot is enabled
    lastDisabled = -1
    lastEnabled = 0
    processSlices = []
    setpointSlices = []
    for i in range(len(fmsMode)):
        if fmsMode["Value"].iloc[i] == True:
            lastEnabled = fmsMode.index[i]
        elif fmsMode["Value"].iloc[i] == False:
            lastDisabled = fmsMode.index[i]
        if lastDisabled > lastEnabled:
            processSlices.append(
                process[
                    (process.index >= lastEnabled) & (process.index <= lastDisabled)
                ]["Value"]
            )
            setpointSlices.append(
                setpoint[
                    (setpoint.index >= lastEnabled) & (setpoint.index <= lastDisabled)
                ]["Value"]
            )
            processSlices.append(process[process.index >= lastEnabled]["Value"])
            setpointSlices.append(setpoint[setpoint.index >= lastEnabled]["Value"])
    if lastDisabled < lastEnabled:
        processSlices.append(process[process.index >= lastEnabled]["Value"])
        setpointSlices.append(setpoint[setpoint.index >= lastEnabled]["Value"])
    processSeries = pd.concat(processSlices)
    setpointSeries = pd.concat(setpointSlices)
    processSeries = processSeries.drop_duplicates()
    setpointSeries = setpointSeries.drop_duplicates()
    # Create dataframe
    df = pd.DataFrame({"Proc": processSeries, "Set": setpointSeries})
    # Interpolate
    df = df.interpolate(limit_process="both")
    # Remove anywhere where the setpoint is 0.
    df = df[df["Set"] != 0.0]
    # Calculate error
    df["Error"] = df["Proc"] - df["Set"]
    # Filter values three standard deviations away from mean and get the maximum
    threeStd = df["Error"].std() * 3
    # Get rid of outliers
    df = df[abs(df["Error"] - df["Error"].mean()) <= threeStd]
    # Get the mean
    mean = df["Error"].mean()
    if mean >= 12:
        return 2, f"{mean} deg/s"
    elif mean >= 6:
        return 1, f"{mean} deg/s"
    if mean < 6:
        return 0, f"{mean} deg/s"

def ProcessMaxCurrent(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the maximum current draw of the arm's motor and uses it to determine a severity.

    Args:
        motorKey: The motor key to check
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    currents = robotTelemetry[robotTelemetry["Key"] == "/arm/motor/current"]
    if currents.empty:
        return -1, "metric_not_implemented"
    currents["Value"] = pd.to_numeric(currents["Value"])
    # Find the mean (using moving average over 1 second)
    maxCurrent = (np.convolve(currents["Value"].to_numpy(), np.ones(50), "valid") / 50).max()
    stoplight = 0
    if maxCurrent > 45:
        stoplight = 2
    elif maxCurrent > 35 and stoplight != 2:
        stoplight = 1
    return stoplight, f"{maxCurrent} A"


def ProcessAverageCurrent(
        robotTelemetry: pd.DataFrame
) -> Tuple[int, str]:
    """Process the average current draw of the arm's motor and uses it to determine a severity.

    Args:
        motorKey: The motor key to check
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    currents = robotTelemetry[robotTelemetry["Key"] == f"/arm/motor/current"]
    if currents.empty:
        return -1, "metric_not_implemented"
    outputs = robotTelemetry[robotTelemetry["Key"] == f"/arm/motor/output"]
    if outputs.empty:
        return -1, "metric_not_implemented"
    currents = pd.to_numeric(currents["Value"])
    outputs = pd.to_numeric(outputs["Value"])
    # Create dataframe
    df = pd.DataFrame({"Out": outputs, "Current": currents})
    # Interpolate
    df = df.interpolate(limit_process="both")
    # Remove anywhere where the output is less than 1%
    df = df[abs(df["Out"]) > 0.01]
    # Find the mean
    avgCurrent = df["Current"].mean()
    stoplight = 0
    if avgCurrent > 10:
        stoplight = 2
    elif avgCurrent > 5 and stoplight != 2:
        stoplight = 1
    return stoplight, f"{avgCurrent} A"

def ProcessMaxMotorTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Checks the temperature of the arm's motor
    Args:
        moduleKey: The key of the motor to check alignment for
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.
    Raises:
        None
    """
    # Grab data
    values = robotTelemetry[robotTelemetry["Key"] == f"/arm/motor/temp"]
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
    """Checks the temperature of the arm's motor
    Args:
        moduleKey: The key of the motor to check alignment for
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.
    Raises:
        None
    """
    # Grab data
    values = robotTelemetry[robotTelemetry["Key"] == f"/arm/motor/temp"]
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