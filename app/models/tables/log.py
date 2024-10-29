from sqlalchemy import (Table, MetaData, Column, Integer, String, Text,
                        DateTime, func)

metadata = MetaData()

logs = Table(
    'logs', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('level', String(50)),
    Column('message', Text),
    Column('timestamp', DateTime, default=func.now())
)