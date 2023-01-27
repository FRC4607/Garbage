from typing import Dict, Tuple
from wpilog.datalog import DataLogReader
from wpilog.dlutil import WPILogToDataFrame
import pkgutil
import importlib
import hashlib
import mmap
from dataclasses import dataclass, field
from db.metric import Metric
from db.engine import engine
from sqlalchemy.orm import Session
@dataclass
class ModuleInfo:
    hash: bytes = bytes()
    metrics: Dict[str, Tuple[int, str]] = field(default_factory=dict)

if __name__ == "__main__":
    file_hash: bytes = bytes([])
    with open("FRC_20221219_235719.wpilog", "r") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        file_hash = hashlib.md5(mm).digest()
        reader = DataLogReader(mm)
        df = WPILogToDataFrame(reader)
    results: Dict[str, ModuleInfo] = {}
    import plugins
    for module in pkgutil.iter_modules(plugins.__path__):
        info = ModuleInfo()
        mod = importlib.import_module(f"plugins.{module.name}")
        with open(mod.__file__, 'rb') as f:
            info.hash = hashlib.file_digest(f, 'md5').digest()
        metrics = mod.defineMetrics()
        for metric in metrics.keys():
            severity, result = metrics[metric](df)
            info.metrics[metric] = (severity, result)
        results[module.name] = info
    rows = []
    for group in results.keys():
        for metric in results[group].metrics.keys():
            severity, result = results[group].metrics[metric]
            rows.append(Metric(
                file_hash=file_hash,
                metric_hash=results[group].hash,
                file_name="FRC_20221219_235719.wpilog",
                group=group,
                metric=metric,
                value=result,
                stoplight=severity
            ))
    print(rows)
    with Session(engine) as sess:
        sess.add_all(rows)
        sess.commit()