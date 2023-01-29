from sqlalchemy import create_engine
from config.parse_args import args
import sys

# Creates the SQAlchemy engine from a DBURL.
try:
    engine = create_engine(args.database)
except:
    print(
        f'Failed to connect to DB with url "{args.database}". Check your connection URL.',
        file=sys.stderr,
    )
    sys.exit(1)
