# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .base import Base
from .poll import Poll
from .result import Result


class User(Base):
    """Table with users"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    polls = relationship(Poll, backref='author', cascade="delete, delete-orphan")
    votes = relationship(Result, backref='user')

    @hybrid_property
    def opened_polls(self):
        return [poll for poll in self.polls if poll.is_open]

    @hybrid_property
    def closed_polls(self):
        return [poll for poll in self.polls if poll.is_closed]
