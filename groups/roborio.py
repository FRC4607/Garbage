from typing import Set, Callable, Tuple, Dict
import pandas as pd
import numpy as np
import scipy

pd.options.mode.chained_assignment = None

boolConv = lambda x: x.replace({"true": 1, "false": 0})


def defineMetrics() -> Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]:
    """Returns a list of the metrics contained in this group and their corresponding functions."""
    return {
        "Brownout Count": ProcessBrownedOut,
        "CAN Utilization": ProcessCanUtilization,
        "CAN Off Count": ProcessCanOffCount,
        "CAN Rx Error Count": ProcessCanRxErrorCount,
        "CAN Tx Error Count": ProcessCanTxErrorCount,
        "Stale DS Data Count": ProcessStaleDsData,
        "IMU Yaw ?Norm Error? P-val": ProcessImuYawAngleNorm,
        "IMU Yaw DpM": ProcessImuYawAngleDrift,
    }


def ProcessBrownedOut(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the RoboRio browned out telemetry data.

    Get the count of brownouts.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    brownOut = robotTelemetry[robotTelemetry["Key"] == "RoboRio Browned Out"]
    if brownOut.empty:
        return -1, "metric_not_implemented"
    brownOut["RoboRio Browned Out"] = boolConv(brownOut["Value"])

    metric = brownOut["RoboRio Browned Out"].sum()
    metricEncoding = 0
    if metric > 1:
        metricEncoding = 2
    elif metric > 0:
        metricEncoding = 1

    return metricEncoding, str(metric)


def ProcessCanUtilization(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the RoboRio CAN utilization telemetry data.

    Take the average of all CAN utilization data and spec that.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    canUtilization = robotTelemetry[robotTelemetry["Key"] == "RoboRio CAN Utilization"]
    if canUtilization.empty:
        return -1, "metric_not_implemented"
    canUtilization["RoboRio CAN Utilization"] = pd.to_numeric(canUtilization["Value"])

    metric = canUtilization["RoboRio CAN Utilization"].mean()
    metricEncoding = 0
    if metric > 80.0:
        metricEncoding = 2
    elif metric > 60.0:
        metricEncoding = 1

    return metricEncoding, str(metric)


def ProcessCanOffCount(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the RoboRio CAN off count telemetry data.

    Filter this to grab the latest output. This will be used to spec the ending count and not used as an event to
    correlate to another metric.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    canOffCount = robotTelemetry[robotTelemetry["Key"] == "RoboRio CAN Off Count"]
    if canOffCount.empty:
        return -1, "metric_not_implemented"
    canOffCount = canOffCount[
        canOffCount["Timestamp"] == canOffCount["Timestamp"].max()
    ]
    canOffCount["RoboRio CAN Off Count"] = pd.to_numeric(canOffCount["Value"])

    metric = canOffCount["RoboRio CAN Off Count"].values[0]
    metricEncoding = 0
    if metric > 5:
        metricEncoding = 2
    elif metric > 0:
        metricEncoding = 1

    return metricEncoding, str(metric)


def ProcessCanRxErrorCount(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the RoboRio CAN receive error count telemetry data.

    Filter this to grab the latest output. This will be used to spec the ending count and not used as an event to
    correlate to another metric.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    canRxErrCount = robotTelemetry[
        robotTelemetry["Key"] == "RoboRio CAN Rx Error Count"
    ]
    if canRxErrCount.empty:
        return -1, "metric_not_implemented"
    canRxErrCount = canRxErrCount[
        canRxErrCount["Timestamp"] == canRxErrCount["Timestamp"].max()
    ]
    canRxErrCount["RoboRio CAN Rx Error Count"] = pd.to_numeric(canRxErrCount["Value"])

    metric = canRxErrCount["RoboRio CAN Rx Error Count"].values[0]
    metricEncoding = 0
    if metric > 5:
        metricEncoding = 2
    elif metric > 0:
        metricEncoding = 1

    return metricEncoding, str(metric)


def ProcessCanTxErrorCount(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the RoboRio CAN transmit error count telemetry data.

    Filter this to grab the latest output. This will be used to spec the ending count and not used as an event to
    correlate to another metric.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    canTxErrCount = robotTelemetry[
        robotTelemetry["Key"] == "RoboRio CAN Tx Error Count"
    ]
    if canTxErrCount.empty:
        return -1, "metric_not_implemented"
    canTxErrCount = canTxErrCount[
        canTxErrCount["Timestamp"] == canTxErrCount["Timestamp"].max()
    ]
    canTxErrCount["RoboRio CAN Tx Error Count"] = pd.to_numeric(canTxErrCount["Value"])

    metric = canTxErrCount["RoboRio CAN Tx Error Count"].values[0]
    metricEncoding = 0
    if metric > 5:
        metricEncoding = 2
    elif metric > 0:
        metricEncoding = 1

    return metricEncoding, str(metric)


def ProcessCanTxFullCount(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the RoboRio CAN transmit full count telemetry data.

    Filter this to grab the latest output. This will be used to spec the ending count and not used as an event to
    correlate to another metric.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        metric: the string label used for displaying the metric in HTML
        metricEncoding: the string encoding used to style the metric in HTML

    Raises:
        None

    """
    canTxFullCount = robotTelemetry[
        robotTelemetry["Key"] == "RoboRio CAN Tx Full Count"
    ]
    if canTxFullCount.empty:
        return -1, "metric_not_implemented"
    canTxFullCount = canTxFullCount[
        canTxFullCount["Timestamp"] == canTxFullCount["Timestamp"].max()
    ]
    canTxFullCount["RoboRio CAN Tx Full Count"] = pd.to_numeric(canTxFullCount["Value"])

    metric = canTxFullCount["RoboRio CAN Tx Full Count"].values[0]
    metricEncoding = 0
    if metric > 5:
        metricEncoding = 2
    elif metric > 0:
        metricEncoding = 1

    return metricEncoding, str(metric)


def ProcessStaleDsData(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the RoboRio stale drivers station telemetry data.

    Count the number of times there is stale data from the drivers station. TODO: this doesn't represent communication
    issues.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    staleDsData = robotTelemetry[robotTelemetry["Key"] == "RoboRio Stale DS Data Count"]
    if staleDsData.empty:
        return -1, "metric_not_implemented"
    staleDsData["RoboRio Stale DS Data Count"] = boolConv(staleDsData["Value"])

    metric = staleDsData["RoboRio Stale DS Data Count"].count()
    metricEncoding = 0
    if metric > 1:
        metricEncoding = 2
    elif metric > 0:
        metricEncoding = 1

    return metricEncoding, str(metric)


def ProcessImuYawAngleNorm(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the IMU yaw angle telemetry data.

    Filter the IMU data to only use the samples collected while the robot is not moving and in a known postion. This
    is determined by using the `FMS Mode` telemetry and using the samples from the first `Disabled` state and the
    minimum of the `Auto` and `Teleop` states.

    Uses this data to determine whether the IMU headings follow a normmal distribution.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    fmsMode = robotTelemetry[robotTelemetry["Key"] == "FMS Mode"]
    if fmsMode.empty:
        return -1, "metric_not_implemented"
    startTime = fmsMode[fmsMode["Value"] == "Disabled"]["Timestamp"].min()
    if startTime.empty:
        return -1, "metric_not_implemented"
    stopTime = fmsMode[fmsMode["Value"].isin(["Teleop", "Auto"])]["Timestamp"].min()
    if stopTime.empty:
        return -1, "metric_not_implemented"
    imuYawAngle = robotTelemetry[robotTelemetry["Key"] == "IMU Yaw Angle (deg)"]
    if imuYawAngle.empty:
        return -1, "metric_not_implemented"
    imuYawAngle = imuYawAngle[
        (imuYawAngle["Timestamp"] <= stopTime) & (imuYawAngle["Timestamp"] >= startTime)
    ]
    imuYawAngle["IMU Yaw Angle (deg)"] = pd.to_numeric(imuYawAngle["Value"])

    # Test for gaussian (gaussian means there is no drift which is good)
    gaussianMetricEncoding = 0
    stat, p = scipy.stats.shapiro(imuYawAngle["IMU Yaw Angle (deg)"].dropna())
    alpha = 0.05  # 95% confidence
    if p > alpha:
        txt = "Gaussian (fail to reject H0), p = %.3f" % (p)
    else:
        gaussianMetricEncoding = 1
        txt = "Not Gaussian (reject H0), p = %.3f" % (p)

    return (gaussianMetricEncoding, txt)


def ProcessImuYawAngleDrift(robotTelemetry: pd.DataFrame) -> Tuple[int, str]:
    """Process the IMU yaw angle telemetry data.

    Filter the IMU data to only use the samples collected while the robot is not moving and in a known postion. This
    is determined by using the `FMS Mode` telemetry and using the samples from the first `Disabled` state and the
    minimum of the `Auto` and `Teleop` states.

    Uses this data to determine whether the IMU headings are severely drifting.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry

    Returns:
        A tuple containing the stoplight severity and a string containing the result of this metric.

    Raises:
        None

    """
    fmsMode = robotTelemetry[robotTelemetry["Key"] == "FMS Mode"]
    if fmsMode.empty:
        return -1, "metric_not_implemented"
    startTime = fmsMode[fmsMode["Value"] == "Disabled"]["Timestamp"].min()
    if startTime.empty:
        return -1, "metric_not_implemented"
    stopTime = fmsMode[fmsMode["Value"].isin(["Teleop", "Auto"])]["Timestamp"].min()
    if stopTime.empty:
        return -1, "metric_not_implemented"
    imuYawAngle = robotTelemetry[robotTelemetry["Key"] == "IMU Yaw Angle (deg)"]
    if imuYawAngle.empty:
        return -1, "metric_not_implemented"
    imuYawAngle = imuYawAngle[
        (imuYawAngle["Timestamp"] <= stopTime) & (imuYawAngle["Timestamp"] >= startTime)
    ]
    imuYawAngle["IMU Yaw Angle (deg)"] = pd.to_numeric(imuYawAngle["Value"])

    linearModel = np.polyfit(
        imuYawAngle["Timestamp"], imuYawAngle["IMU Yaw Angle (deg)"], 1
    )
    predictor = np.poly1d(linearModel)
    imuYawAngle["Linear Regression"] = predictor(imuYawAngle["Timestamp"])
    driftDegPerMinMetricEncoding = 0
    driftDegPerMin = abs(linearModel[0] * 60.0)
    if driftDegPerMin > 1.0:
        driftDegPerMinMetricEncoding = 2
    elif driftDegPerMin > 0.5:
        driftDegPerMinMetricEncoding = 1

    return driftDegPerMinMetricEncoding, str(driftDegPerMin)
