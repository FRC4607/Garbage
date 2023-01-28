import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from db.engine import engine
import datetime


class Base(DeclarativeBase):
    """The base for all of the tables in the database."""

    pass


class Metric(Base):
    """The results of one specific metric ran against a specific log file."""

    __tablename__ = "metrics"
    id: Mapped[int] = mapped_column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    file_hash: Mapped[bytes] = mapped_column(sqlalchemy.BINARY(16), nullable=False)
    metric_hash: Mapped[bytes] = mapped_column(sqlalchemy.BINARY(16), nullable=False)
    file_name: Mapped[str] = mapped_column(sqlalchemy.Unicode(1024), nullable=False)
    group: Mapped[str] = mapped_column(sqlalchemy.Unicode(1024), nullable=False)
    metric: Mapped[str] = mapped_column(sqlalchemy.Unicode(1024), nullable=False)
    value: Mapped[str] = mapped_column(sqlalchemy.Unicode(1024), nullable=False)
    stoplight: Mapped[int] = mapped_column(sqlalchemy.SmallInteger, nullable=False)
    metric_timestamp: Mapped[datetime.datetime] = mapped_column(
        sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()
    )


Base.metadata.create_all(engine)
