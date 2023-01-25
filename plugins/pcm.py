import pandas as pd
from typing import Callable, Dict, Tuple
pd.options.mode.chained_assignment = None

def defineMetrics() -> Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]:
    return {
        "Starting Pressure": ProcessPressure,
        "Max Compressor Current": ProcessCompressorCurrent,
    }

def ProcessPressure(robotTelemetry: pd.DataFrame):
    ''' Process the pneumatics hub pressure telemetry data.

    Spec the pressure when the robot is first enabled. This will check that the pneumatics were charged up in the pit
    or queue.

    TODO: Check and spec the pressure at the beginning of auto. Check and spec an average pressure for teleop. Check
    and spec pressue at the beginning of the end game.


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
    pressure = robotTelemetry[robotTelemetry['Key'] == 'Pressure (psi)']
    if pressure.empty:
        return -1, 'metric_not_implemented'
    pressure['Pressure (psi)'] = pd.to_numeric(pressure['Value'])
    metric = pressure['Pressure (psi)'].iloc[0]
    metricEncoding = 0
    if metric < 80.0:
        metricEncoding = 2
    elif metric < 100.0:
        metricEncoding = 1

    return metricEncoding, str(metric)


def ProcessCompressorCurrent(robotTelemetry: pd.DataFrame):
    ''' Process the pneumatics hub compresoor current telemetry data.

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
    current = robotTelemetry[robotTelemetry['Key'] == 'Compressor Current (A)']
    if current.empty:
        return -1, 'metric_not_implemented'
    current['Compressor Current (A)'] = pd.to_numeric(current['Value'])

    metric = current['Compressor Current (A)'].max()
    metricEncoding = 0
    if metric > 20.0:
        metricEncoding = 2
    elif metric > 16.0:
        metricEncoding = 1

    return metricEncoding, metric
