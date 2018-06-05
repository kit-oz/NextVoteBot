# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from .base import Base
from .result import Result


class Choice(Base):
    """Table with answers to polls"""
    __tablename__ = 'choice'
    id = Column(Integer, primary_key=True)
    text = Column(String(250))

    poll_id = Column(Integer, ForeignKey('poll.id'))

    results = relationship(Result, backref='choice', cascade="delete, delete-orphan")
