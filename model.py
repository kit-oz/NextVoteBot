# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from config import POLL_CODE_LENGTH, SQLALCHEMY_DATABASE_URI, WAIT_QUESTION, VISIBLE_AFTER_ANSWER, POLL_OPEN


engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    state = Column(Integer, default=WAIT_QUESTION)


class Poll(Base):
    __tablename__ = 'poll'
    id = Column(String(POLL_CODE_LENGTH), primary_key=True)
    question = Column(String(250))
    date = Column(DateTime, default=datetime.utcnow)
    state = Column(Integer, default=POLL_OPEN)
    result_visible = Column(Integer, default=VISIBLE_AFTER_ANSWER)
    can_change_answer = Column(Boolean, default=True)

    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship(User, backref='polls')


class Choice(Base):
    __tablename__ = 'choice'
    id = Column(Integer, primary_key=True)
    text = Column(String(250))

    poll_id = Column(Integer, ForeignKey('poll.id'))
    poll = relationship(Poll, backref='choices')


class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref='results')
    poll_id = Column(Integer, ForeignKey('poll.id'))
    poll = relationship(Poll, backref='results')
    choice_id = Column(Integer, ForeignKey('choice.id'))
    choice = relationship(Choice, backref='results')
