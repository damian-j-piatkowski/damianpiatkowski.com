from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Text, DateTime
)
from sqlalchemy.sql import func

metadata = MetaData()

logs = Table(
    'logs', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('level', String(50), nullable=False),
    Column('message', Text, nullable=False),
    Column(
        'timestamp',
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()  # Use SQLAlchemy's server-side default for UTC timestamp
    )
)
