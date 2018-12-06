from sqlalchemy import create_engine, VARCHAR, MetaData, Text, Table, Integer, String, Column, DateTime, ForeignKey, Numeric, CheckConstraint
import os
from datetime import datetime

metadata = MetaData()


def get_engine():
    engine = create_engine(
        os.environ['DATABASE_URL'], encoding="utf8")
    return engine


users = Table('users', metadata,
              Column('id', Integer(), primary_key=True, autoincrement=True),
              Column('email', String(2083), nullable=False),
              Column('password', String(2083), nullable=False),
              Column('created_on', DateTime(), default=datetime.now),
              Column('updated_on', DateTime(),
                     default=datetime.now, onupdate=datetime.now)
              )

sources = Table('sources', metadata,
                Column('id', Integer(), primary_key=True),
                Column('name', String(100), nullable=False),
                Column('url', VARCHAR(900),  unique=True, nullable=False),
                Column('created_on', DateTime(), default=datetime.now),
                Column('updated_on', DateTime(),
                       default=datetime.now, onupdate=datetime.now)
                )


articles = Table('articles', metadata,
                 Column('id', Integer(), primary_key=True),
                 Column('author', Text(), nullable=True),
                 Column('title', Text(), nullable=True),
                 Column('original_title', String(200), nullable=True),
                 Column('url', VARCHAR(900),  unique=True, nullable=False),
                 Column('top_image', String(2083),  nullable=True),
                 Column('keywords', Text(), nullable=True),
                 Column('original_text', Text(), nullable=True),
                 Column('text', Text(), nullable=True),
                 Column('top_image', Text(), nullable=True),
                 Column('summary', Text(), nullable=True),
                 Column('date', DateTime(), nullable=True),
                 Column('created_on', DateTime(), default=datetime.now),
                 Column('updated_on', DateTime(),
                        default=datetime.now, onupdate=datetime.now)
                 )


metadata.create_all(get_engine())
