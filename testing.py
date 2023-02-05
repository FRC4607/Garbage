import pandas as pd
import numpy as np
import scipy.signal
import mmap
from wpilog.datalog import DataLogReader
from wpilog.dlutil import WPILogToDataFrame
from typing import Dict, List, Tuple
import math
import matplotlib.pyplot as plt


def _getImuYawAngle(gyroKey: str, robotTelemetry: pd.DataFrame) -> pd.DataFrame:
    fmsMode = robotTelemetry[robotTelemetry["Key"] == "DS:enabled"]
    if fmsMode.empty:
        return -1, "metric_not_implemented"
    stopTime = fmsMode[fmsMode["Value"] == True].index.min()
    imuYawAngle = robotTelemetry[robotTelemetry["Key"] == f"swerve/{gyroKey}/yaw"]
    if imuYawAngle.empty:
        return -1, "metric_not_implemented"
    imuYawAngle = imuYawAngle[
        (imuYawAngle.index <= stopTime)
    ]
    imuYawAngle["IMU Yaw Angle (deg)"] = pd.to_numeric(imuYawAngle["Value"])
    return imuYawAngle


with open("archive\\logs\\FRC_20230204_221335.wpilog", "r") as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    reader = DataLogReader(mm)
    df = WPILogToDataFrame(reader)

print(_getImuYawAngle("pigeon", df))
