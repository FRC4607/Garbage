from sqlalchemy import create_engine

# Creates the SQAlchemy engine from a DBURL.
engine = create_engine("mysql+pymysql://root:4607@localhost/garbage?charset=utf8mb4")
