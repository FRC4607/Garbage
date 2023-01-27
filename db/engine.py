from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:4607@localhost/garbage?charset=utf8mb4')