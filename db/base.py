# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URI

Session = scoped_session(sessionmaker())


class BaseMixin(object):
    query = Session.query_property()

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


engine = create_engine(DATABASE_URI)
engine.echo = True

# Base = declarative_base(cls=BaseMixin)
Base = declarative_base()
Base.metadata.bind = engine

Session.configure(bind=engine)
