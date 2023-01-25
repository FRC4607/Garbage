from typing import Dict, Tuple
from wpilog.datalog import DataLogReader
from wpilog.dlutil import WPILogToDataFrame
import pkgutil
import importlib

if __name__ == "__main__":
    import mmap
    with open("FRC_20221219_235719.wpilog", "r") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        reader = DataLogReader(mm)
        df = WPILogToDataFrame(reader)
    results: Dict[str, Dict[str, Tuple[int, str]]] = {}
    import plugins
    for module in pkgutil.iter_modules(plugins.__path__):
        mod = importlib.import_module(f"plugins.{module.name}")
        tests = mod.defineMetrics()
        for test in tests.keys():
            severity, result = tests[test](df)
            if module.name not in results.keys():
                results[module.name] = {}
            results[module.name][test] = (severity, result)
    print(results)