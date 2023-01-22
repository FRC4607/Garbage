from typing import Dict, Tuple
import pandas as pd
import numpy as np
from dataanalysis.datalog import DataLogReader, StartRecordData
    
def WPILogToDataFrame(log: DataLogReader) -> pd.DataFrame:
    records: Dict[int, Tuple[StartRecordData, pd.Series]] = {}

    for record in log:
        if record.isStart:
            startRecord = record.getStartData()
            records[startRecord.entry]
        