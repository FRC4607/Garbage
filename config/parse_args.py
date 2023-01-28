import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-d",
    "--database",
    help="A SQAlchemy connection string that specifies the database to connect to.",
)

parser.add_argument(
    "-m",
    "--metrics",
    help="The directory where the files containing the metrics are stored.",
)

parser.add_argument("log", help="The path to the log file to run the metrics on.")
