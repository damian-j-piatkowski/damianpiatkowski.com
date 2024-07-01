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

blog_posts = Table(
    'blog_posts', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('content', Text, nullable=False),
    Column('image_small', String(255)),
    Column('image_medium', String(255)),
    Column('image_large', String(255))
)
