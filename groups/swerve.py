from typing import Set, Callable, Tuple, Dict
import pandas as pd
import numpy as np
import scipy
import math

pd.options.mode.chained_assignment = None

boolConv = lambda x: x.replace({"true": 1, "false": 0})


def defineMetrics() -> Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]:
    """Returns a list of the metrics contained in this group and their corresponding functions."""
    return {
        "FL Turning Encoder Alignment": ProcessFrontLeftTurningEncoderAlignment,
        "FL Drive Motor Max Temp": ProcessFrontLeftDriveMaxTemp,
        "FL Turn Motor Max Temp": ProcessFrontLeftTurnMaxTemp,
        "FL Turn Motor Mean Error": ProcessFrontLeftTurnMeanError,
        "FL Drive Motor Mean Error": ProcessFrontLeftDriveMeanError,
        "FR Turning Encoder Alignment": ProcessFrontRightTurningEncoderAlignment,
        "FR Drive Motor Max Temp": ProcessFrontRightDriveMaxTemp,
        "FR Turn Motor Max Temp": ProcessFrontRightTurnMaxTemp,
        "FR Turn Motor Mean Error": ProcessFrontRightTurnMeanError,
        "FR Drive Motor Mean Error": ProcessBackLeftDriveMeanError,
        "BL Turning Encoder Alignment": ProcessBackLeftTurningEncoderAlignment,
        "BL Drive Motor Max Temp": ProcessBackLeftDriveMaxTemp,
        "BL Turn Motor Max Temp": ProcessBackLeftTurnMaxTemp,
        "BL Turn Motor Mean Error": ProcessBackLeftTurnMeanError,
        "BL Drive Motor Mean Error": ProcessBackLeftDriveMeanError,
        "BR Turning Encoder Alignment": ProcessBackRightTurningEncoderAlignment,
        "BR Drive Motor Max Temp": ProcessBackRightDriveMaxTemp,
        "BR Turn Motor Max Temp": ProcessBackRightTurnMaxTemp,
        "BR Turn Motor Mean Error": ProcessBackRightTurnMeanError,
        "BR Drive Motor Mean Error": ProcessBackRightDriveMeanError,
    }


def ProcessFrontLeftTurningEncoderAlignment(
    robotTelemetry: pd.DataFrame,
) -> Tuple[int, str]:
    return ProcessTurningEncoderAlignment("Front Left", robotTelemetry)


def ProcessFrontLeftDriveMaxTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessMaxMotorTemp("Front Left/drive", robotTelemetry)


def ProcessFrontLeftTurnMaxTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessMaxMotorTemp("Front Left/turn", robotTelemetry)


def ProcessFrontLeftDriveMeanError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessDriveMotorMeanError("Front Left/drive", robotTelemetry)


def ProcessFrontLeftTurnMeanError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessTurnMotorMeanError("Front Left/turn", robotTelemetry)


def ProcessFrontRightTurningEncoderAlignment(
    robotTelemetry: pd.DataFrame,
) -> Tuple[int, str]:
    return ProcessTurningEncoderAlignment("Front Right", robotTelemetry)


def ProcessFrontRightDriveMaxTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessMaxMotorTemp("Front Right/drive", robotTelemetry)


def ProcessFrontRightTurnMaxTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessMaxMotorTemp("Front Right/turn", robotTelemetry)


def ProcessFrontRightDriveMeanError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessDriveMotorMeanError("Front Right/drive", robotTelemetry)


def ProcessFrontRightTurnMeanError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessTurnMotorMeanError("Front Right/turn", robotTelemetry)


def ProcessBackLeftTurningEncoderAlignment(
    robotTelemetry: pd.DataFrame,
) -> Tuple[int, str]:
    return ProcessTurningEncoderAlignment("Back Left", robotTelemetry)


def ProcessBackLeftDriveMaxTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessMaxMotorTemp("Back Left/drive", robotTelemetry)


def ProcessBackLeftTurnMaxTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessMaxMotorTemp("Back Left/turn", robotTelemetry)


def ProcessBackLeftDriveMeanError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessDriveMotorMeanError("Back Left/drive", robotTelemetry)


def ProcessBackLeftTurnMeanError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessTurnMotorMeanError("Back Left/turn", robotTelemetry)


def ProcessBackRightTurningEncoderAlignment(
    robotTelemetry: pd.DataFrame,
) -> Tuple[int, str]:
    return ProcessTurningEncoderAlignment("Back Right", robotTelemetry)


def ProcessBackRightDriveMaxTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessMaxMotorTemp("Back Right/drive", robotTelemetry)


def ProcessBackRightTurnMaxTemp(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessMaxMotorTemp("Back Right/turn", robotTelemetry)


def ProcessBackRightDriveMeanError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessTurnMotorMeanError("Back Right/drive", robotTelemetry)


def ProcessBackRightTurnMeanError(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    return ProcessTurnMotorMeanError("Back Right/turn", robotTelemetry)


def ProcessTurningEncoderAlignment(
    moduleKey: str, robotTelemetry: pd.DataFrame
) -> Tuple[int, str]:
    # Grab data
    neoEncoder = robotTelemetry[
        robotTelemetry["Key"] == f"/swerve/{moduleKey}/turn/position"
    ]
    if neoEncoder.empty:
        return -1, "metric_not_implemented"
    absEncoder = robotTelemetry[
        robotTelemetry["Key"] == f"/swerve/{moduleKey}/turn_enc/absolute"
    ]
    if absEncoder.empty:
        return -1, "metric_not_implemented"
    homes = robotTelemetry[robotTelemetry["Key"] == f"/swerve/{moduleKey}/home"]
    if homes.empty:
        return -1, "metric_not_implemented"
    # Cut out the garbage data at the beginning
    neoEncoder = neoEncoder.iloc[10:]
    absEncoder = absEncoder.iloc[10:]
    # Convert to numerics
    neoEncoder["Value"] = pd.to_numeric(neoEncoder["Value"])
    absEncoder["Value"] = pd.to_numeric(absEncoder["Value"])
    homes["Value"] = pd.to_numeric(homes["Value"])
    # Trim to smallest list
    minLen = min(len(neoEncoder), len(absEncoder))
    neoEncoder = neoEncoder.iloc[:minLen]
    absEncoder = absEncoder.iloc[:minLen]
    # Home offsets
    prevStart = 0
    for i in range(len(homes)):
        if prevStart != 0:
            absEncoder.update(
                absEncoder[
                    (absEncoder.index >= prevStart)
                    & (absEncoder.index < homes.index[i])
                ]["Value"]
                - homes["Value"].iloc[i]
            )
        prevStart = homes.index[i]
    absEncoder.update(
        absEncoder[absEncoder.index >= prevStart]["Value"]
        - homes["Value"].iloc[len(homes) - 1]
    )
    # Convert to one dataframe
    test = pd.DataFrame({"ABS": absEncoder["Value"], "NEO": neoEncoder["Value"]})
    # Interpolate
    test = test.interpolate(limit_direction="both")
    # Compute error
    test["Error"] = (test["ABS"] - test["NEO"]).abs()
    # Get rid of values three standard deviations away from the mean
    threeStd = test["Error"].std() * 3
    errorsFilt = test[abs(test["Error"] - test["Error"].mean()) <= threeStd]["Error"]
    # Get the maximum error
    maxError = errorsFilt.max()
    # Calculate stoplight
    stoplight = 0
    if maxError > math.radians(5):
        stoplight = 2
    elif maxError > math.radians(3) and stoplight == 0:
        stoplight = 1
    return stoplight, f"{str(maxError)} rad"


def ProcessMaxMotorTemp(motorKey: str, robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    # Grab data
    values = robotTelemetry[robotTelemetry["Key"] == f"/swerve/{motorKey}/temp"]
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
    return stoplight, str(maxTemp)


def ProcessMeanMotorError(
    procesKey: str, setpointKey: str, robotTelemetry: pd.DataFrame
) -> float:
    # Grab data
    process = robotTelemetry[robotTelemetry["Key"] == f"/swerve/{procesKey}"]
    if process.empty:
        return np.nan
    setpoint = robotTelemetry[robotTelemetry["Key"] == f"/swerve/{setpointKey}"]
    if setpoint.empty:
        return np.nan
    fmsMode = robotTelemetry[robotTelemetry["Key"] == "DS:enabled"]
    if fmsMode.empty:
        return np.nan
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
    # Calculate error
    df["Error"] = df["Proc"] - df["Set"]
    # Filter values three standard deviations away from mean and get the maximum
    threeStd = df["Error"].std() * 3
    # Get rid of outliers
    df = df[abs(df["Error"] - df["Error"].mean()) <= threeStd]
    # Get the mean
    return df["Error"].mean()


def ProcessDriveMotorMeanError(
    moduleKey: str, robotTelemetry: pd.DataFrame
) -> Tuple[int, str]:
    mean = abs(
        ProcessMeanMotorError(
            f"/swerve/{moduleKey}/drive/velocity",
            f"/swerve/{moduleKey}/drive/setpoint",
            robotTelemetry,
        )
    )
    stoplight = 0
    if mean > 0.1:
        stoplight = 2
    if mean > 0.05 and stoplight == 0:
        stoplight = 1
    return stoplight, f"{str(mean)} m/s"


def ProcessTurnMotorMeanError(
    moduleKey: str, robotTelemetry: pd.DataFrame
) -> Tuple[int, str]:
    mean = abs(
        ProcessMeanMotorError(
            f"/swerve/{moduleKey}/turn/position",
            f"/swerve/{moduleKey}/drive/setpoint",
            robotTelemetry,
        )
    )
    if np.isnan(mean):
        return -1, "metric_not_implemented"
    stoplight = 0
    if mean > math.radians(3):
        stoplight = 2
    if mean > math.radians(2) and stoplight == 0:
        stoplight = 1
    return stoplight, f"{str(mean)} rad"
