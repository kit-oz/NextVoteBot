# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from .base import Base


class Result(Base):
    """Table with users answers"""
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('user.id'))
    choice_id = Column(Integer, ForeignKey('choice.id'))
