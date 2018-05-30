# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URI


engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    """Table with users"""
    __tablename__ = 'user'

    # User states
    WRITE_QUESTION = 0
    WRITE_FIRST_ANSWER = 1
    WRITE_OTHER_ANSWER = 2

    id = Column(Integer, primary_key=True)
    state = Column(Integer, default=WRITE_QUESTION)

    def is_author(self, poll):
        return self.id == poll.user_id

    def is_write_question(self):
        return self.state == self.WRITE_QUESTION

    def is_write_first_answer(self):
        return self.state == self.WRITE_FIRST_ANSWER

    def is_write_other_answer(self):
        return self.state == self.WRITE_OTHER_ANSWER


class Poll(Base):
    """Table with polls"""
    __tablename__ = 'poll'

    # Poll states
    OPEN = 0
    CLOSED = 1
    DELETED = 2

    # Results visibility options
    RESULT_VISIBLE_NEVER = 0
    RESULT_VISIBLE_AFTER_ANSWER = 1
    RESULT_VISIBLE_ALWAYS = 2

    CODE_LENGTH = 7

    id = Column(String(CODE_LENGTH), primary_key=True)
    question = Column(String(250))
    date = Column(DateTime, default=datetime.utcnow)
    state = Column(Integer, default=OPEN)
    result_visible = Column(Integer, default=RESULT_VISIBLE_AFTER_ANSWER)
    can_change_answer = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref='polls')

    def is_open(self):
        return self.state == self.OPEN

    def is_closed(self):
        return self.state == self.CLOSED

    def is_deleted(self):
        return self.state == self.DELETED

    def is_result_visible_always(self):
        return self.result_visible == self.RESULT_VISIBLE_ALWAYS

    def is_result_visible_after_answer(self):
        return self.result_visible == self.RESULT_VISIBLE_AFTER_ANSWER


class Choice(Base):
    """Table with answers to polls"""
    __tablename__ = 'choice'
    id = Column(Integer, primary_key=True)
    text = Column(String(250))

    poll_id = Column(Integer, ForeignKey('poll.id'))
    poll = relationship(Poll, backref='choices')


class Result(Base):
    """Table with users answers"""
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref='results')
    poll_id = Column(Integer, ForeignKey('poll.id'))
    poll = relationship(Poll, backref='results')
    choice_id = Column(Integer, ForeignKey('choice.id'))
    choice = relationship(Choice, backref='results')


Base.metadata.create_all(engine)
