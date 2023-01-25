import pandas as pd
from typing import Callable, Dict, Tuple
pd.options.mode.chained_assignment = None

def defineMetrics() -> Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]:
    return {
        "Starting Voltage": ProcessStartingVoltage,
        "Ending Voltage": ProcessEndingVoltage,
    }

def ProcessStartingVoltage(robotTelemetry: pd.DataFrame):
    voltage = robotTelemetry[robotTelemetry['Key'] == 'PDH Input Voltage (V)']
    if voltage.empty:
        return -1, 'metric_not_implemented'
    voltage['PDH Input Voltage (V)'] = pd.to_numeric(voltage['Value'])

    startVoltage = voltage['PDH Input Voltage (V)'].iloc[0]
    startVoltageMetricEncoding = 0
    if startVoltage < 11.5:
        startVoltageMetricEncoding = 2
    elif startVoltage < 11.7:
        startVoltageMetricEncoding = 1

    return startVoltageMetricEncoding, str(startVoltage)

def ProcessEndingVoltage(robotTelemetry: pd.DataFrame):
    ''' Process the power distribution hub pressure telemetry data.

    Args:
        robotTelemetry: Pandas dataframe of robot telemetry
        key: the telemetry key
        cFunc: the conversion function for the `Value` column

    Returns:
        metric: the string label used for displaying the metric in HTML
        metricEncoding: the string encoding used to style the metric in HTML

    Raises:
        None

    '''
    voltage = robotTelemetry[robotTelemetry['Key'] == 'PDH Input Voltage (V)']
    if voltage.empty:
        return -1, 'metric_not_implemented'
    voltage['PDH Input Voltage (V)'] = pd.to_numeric(voltage['Value'])

    endVoltage = voltage['PDH Input Voltage (V)'].iloc[-1]
    endVoltageMetricEncoding = 0
    if endVoltage < 11.0:
        endVoltageMetricEncoding = 2
    elif endVoltage < 11.2:
        endVoltageMetricEncoding = 1

    return endVoltageMetricEncoding, str(endVoltage)
