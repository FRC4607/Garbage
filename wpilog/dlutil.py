from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from wpilog.datalog import DataLogReader, StartRecordData, WPILogEntryToType, WPILogToDtype
    
def WPILogToDataFrame(log: DataLogReader) -> pd.DataFrame:
    """
    Takes a DataLogReader as input and produces a pandas dataframe with timestamps as
    an index and log path names as columns.

    Arguments:
    log: The DataLogReader to read from.

    Returns:
    A dataframe with data from the log file.
    """
    # Define some variables
    startRecords: Dict[int, StartRecordData] = {}
    types: Dict[str, Any] = {}
    rows: List[Tuple[int, str, any]] = []

    print("Iterating records...")

    # Iterate over records in the log
    for record in log:
        if record.isStart():
            startRecord: StartRecordData = record.getStartData()
            startRecords[startRecord.entry] = startRecord
        if not record.isControl():
            startRecord = startRecords[record.entry]
            rows.append((record.timestamp, startRecord.name, WPILogEntryToType(startRecord, record)))
            types[startRecord.name] = WPILogToDtype(startRecord.type)

    print("Constructing dataframe...")

    # Constrct a DF, flip it
    df = pd.DataFrame(rows, columns=["Timestamp", "Key", "Value"])
    
    df = df.set_index("Timestamp")
    df = df.pivot(columns="Key", values="Value")

    print("Converting number types to numbers. This may take a while...")

    # Convert all of the numbers to numbers
    colList = df.columns.to_list()
    colList = list(filter(lambda c: types[c] in [np.float64, pd.Int64Dtype()], colList))
    if "systemTime" in colList:
        colList.remove("systemTime")
    cols = df.columns.isin(colList)
    df[df.columns[cols]] = df[df.columns[cols]].apply(pd.to_numeric, axis=1)

    print("Setting dtypes...")

    # Set dtypes
    types["systemTime"] = "datetime64[us]"
    df = df.astype(types)

    return df        