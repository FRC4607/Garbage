from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datalog import DataLogReader, StartRecordData, WPILogToDtype, WPILogEntryToType
    
def WPILogToDataFrame(log: DataLogReader) -> pd.DataFrame:
    recordEntries: Dict[int, Tuple[StartRecordData, List[Any]]] = {}

    for record in log:
        if record.isStart():
            startRecord: StartRecordData = record.getStartData()
            recordEntries[startRecord.entry]
        if not record.isControl():
            recordEntries[record.entry].append(WPILogEntryToType(record))
            print(recordEntries[record.entry])