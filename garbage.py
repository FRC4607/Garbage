from typing import Dict, List, Tuple
from wpilog.datalog import DataLogReader
from wpilog.dlutil import WPILogToDataFrame
import pkgutil
import importlib
import importlib.util
import hashlib
import mmap
from dataclasses import dataclass, field
from db.metric import Metric
from db.engine import engine
from sqlalchemy.orm import Session
from sqlalchemy import Select
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileMovedEvent, FileSystemEventHandler
import os
import sys
from config.parse_args import args, logsPath, metricsPath
import json
import datetime


@dataclass
class LogFileInfo:
    """A class that stores information from a log file's name."""

    fileName: str = ""
    dt: datetime.datetime = None
    event: str = None
    matchInfo: str = None


def getInfoFromLogName(name: str) -> LogFileInfo:
    # Split up the filename into its useful parts
    parts = name.split("_")
    temp = parts[-1]
    del parts[-1]
    parts.append(temp.split(".")[0])
    # If this log was never updated with time/match info, exit.
    if parts[1] == "TBD":
        return LogFileInfo(fileName=name)
    # Calculate this log's datetime and then convert it to the local time.
    dt = (
        datetime.datetime.strptime(f"{parts[1]}_{parts[2]}", "%Y%m%d_%H%M%S")
        .replace(tzinfo=datetime.timezone.utc)
        .astimezone()
    )
    print(dt)
    # If our log is just a datetime, return that.
    if len(parts) == 3:
        return LogFileInfo(fileName=name, dt=dt)
    # Return the event ID and match info
    return LogFileInfo(fileName=name, dt=dt, event=parts[3], matchInfo=parts[4])


def analyze_and_upload(path: str):
    print(f'Starting analysis of "{path}".')
    # Open the log file and take its hash.
    file_hash: bytes = bytes([])
    try:
        with open(path, "r") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            file_hash = hashlib.md5(mm).digest()
            reader = DataLogReader(mm)
            df = WPILogToDataFrame(reader)
    except:
        print(f"Opening of {path} failed. Skipping.")
        return

    # Do this after we open the file to make sure the file format
    info = getInfoFromLogName(os.path.basename(path))

    # Loop over each module/group and run its metrics.
    results: Dict[str, GroupInfo] = {}

    try:
        for group in groupsList:
            # Reset the metrics dictionary
            group.metrics = {}

            # Check to see if we have already ran the same metrics on the same log.
            with open(group.module.__file__, "rb") as f:
                group.hash = hashlib.file_digest(f, "md5").digest()
            with Session(engine) as sess:
                statement = (
                    Select(Metric.id)
                    .where(Metric.file_hash == file_hash)
                    .where(Metric.metric_hash == group.hash)
                )
                prevMetrics = sess.scalar(statement)

            if prevMetrics is None:
                # Run the metrics and store them
                metrics = group.module.defineMetrics()
                for metric in metrics.keys():
                    severity, result = metrics[metric](df)
                    group.metrics[metric] = (severity, result)
                results[group.name] = group
            else:
                print(
                    f'Metrics in group "{group.name}" already ran on this file. Skipping.'
                )
                return
    except:
        print(f"Metrics failed to run on file {path}. Skipping.")
        return

    # Convert metrics to JSON
    try:
        jFilePath = ""
        jDict: Dict[str, Dict] = {"hash": file_hash.hex()}
        for key in results.keys():
            jDict[key] = {
                "hash": results[key].hash.hex(),
                "metrics": results[key].metrics,
            }

        jString = json.dumps(jDict)
        if jString != "":
            jFilePath = os.path.join(
                metricsPath,
                f"{info.fileName.replace('.', '_')}"
                + "_"
                + f"{str(datetime.datetime.today()).replace(' ', '_').replace('.', '-').replace(':', '-')}"
                + ".json",
            )
            print(f'Writing metric JSON to "{jFilePath}".')
            with open(jFilePath, "w") as f:
                f.write(jString)
    except:
        print(f"Conversion of metric on {path} to JSON failed. Skipping.")
        return

    # Create DB rows by looping over all metrics and store them in the table
    try:
        rows = []
        for group in results.keys():
            for metric in results[group].metrics.keys():
                severity, result = results[group].metrics[metric]
                rows.append(
                    Metric(
                        file_hash=file_hash,
                        metric_hash=results[group].hash,
                        file_name=info.fileName,
                        group=group,
                        metric=metric,
                        value=result,
                        stoplight=severity,
                        log_timestamp=info.dt,
                        event_key=info.event,
                        match_info=info.matchInfo,
                    )
                )
        with Session(engine) as sess:
            sess.add_all(rows)
            sess.commit()
    except:
        print(
            f"Addition of metrics of {path} to database failed. Metrics can be found in {jFilePath} (if blank, no JSON created)."
        )

    print(f'Analysis of "{path}" completed with {len(rows)} metrics computed.')


class LogFileWatcher(FileSystemEventHandler):
    """A class that watches for changes in the log file directory and causes an analysis if there are any."""

    def on_created(self, e: FileCreatedEvent):
        print(f'Update of "{e.src_path}" detected.')
        analyze_and_upload(e.src_path)

    def on_moved(self, e: FileMovedEvent):
        print(f'Update of "{e.dest_path}" detected.')
        analyze_and_upload(e.dest_path)


@dataclass
class GroupInfo:
    """Stores info about each module that's imported."""

    name: str = ""
    hash: bytes = bytes()
    module: pkgutil.ModuleInfo = None
    metrics: Dict[str, Tuple[int, str]] = field(default_factory=dict)


if __name__ == "__main__":
    # Cache all of the groups
    groupsList: List[GroupInfo] = []
    for group in os.listdir(args.groups):
        try:
            if group != "__pycache__":
                # Take the hash of the module's source code.
                modName = group.split(".")[0]
                s = importlib.util.spec_from_file_location(
                    modName, os.path.join(args.groups, group)
                )
                mod = importlib.util.module_from_spec(s)
                sys.modules[modName] = mod
                s.loader.exec_module(mod)
                with open(mod.__file__, "rb") as f:
                    hash = hashlib.file_digest(f, "md5").digest()
                groupsList.append(GroupInfo(name=modName, hash=hash, module=mod))
        except:
            print(f"Error importing file {group} in {args.groups}.", file=sys.stderr)
            sys.exit(1)

    # If the user wants to rescan, do that
    if args.rescan:
        logs = os.listdir(logsPath)
        print(f"Starting rescan of {len(logs)} logs.")
        for log in logs:
            analyze_and_upload(os.path.join(logsPath, log))

    # Start main loop
    o: Observer = Observer()
    handler = LogFileWatcher()
    o.schedule(handler, "./archive/logs/")
    o.start()
    print(
        f'Garbage started with {len(groupsList)} groups. Move log files into "{str(logsPath)}" to analyze.'
    )
    try:
        while o.is_alive():
            o.join(1)
    finally:
        o.stop()
        o.join()
