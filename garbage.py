from wpilog.datalog import DataLogReader
from wpilog.dlutil import WPILogToDataFrame

if __name__ == "__main__":
    import mmap
    with open("FRC_20221219_235719.wpilog", "r") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        reader = DataLogReader(mm)
        df = WPILogToDataFrame(reader)