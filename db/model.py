# -*- coding: utf-8 -*-

import random
import string

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
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

    id = Column(Integer, primary_key=True)

    polls = relationship(Poll, backref='author')

    @hybrid_property
    def opened_polls(self):
        return [poll for poll in self.polls if poll.is_open()]

    @hybrid_property
    def closed_polls(self):
        return [poll for poll in self.polls if poll.is_closed()]


class Poll(Base):
    """Table with polls"""
    __tablename__ = 'poll'

    # Poll states
    DRAFT = 0
    OPEN = 1
    CLOSED = 2
    DELETED = 3

    # Results visibility options
    RESULT_VISIBLE_NEVER = 0
    RESULT_VISIBLE_AFTER_ANSWER = 1
    RESULT_VISIBLE_ALWAYS = 2

    CODE_LENGTH = 7

    id = Column(String(CODE_LENGTH), primary_key=True)

    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))

    question = Column(String(250))
    choices = relationship("Choice", back_populates='poll', cascade="all, delete, delete-orphan")

    state = Column(Integer, default=DRAFT)
    result_visible = Column(Integer, default=RESULT_VISIBLE_AFTER_ANSWER)
    can_change_answer = Column(Boolean, default=True)

    def __init__(self, user, question):
        while True:
            new_code = ''.join(random.choice(string.ascii_letters + string.digits)
                               for _ in range(self.CODE_LENGTH))
            poll_with_code = session.query(Poll).get(new_code)
            if not poll_with_code:
                break

        self.id = new_code
        self.user_id = user.id
        self.question = question

    @hybrid_property
    def is_closed(self):
        return self.state == self.CLOSED

    @hybrid_property
    def is_deleted(self):
        return self.state == self.DELETED

    @hybrid_property
    def is_draft(self):
        return self.state == self.DRAFT

    @is_draft.expression
    def is_draft(cls):
        return select(cls).where(cls.state == cls.DRAFT)
        # return cls.state == cls.DRAFT

    @hybrid_property
    def is_open(self):
        return self.state == self.OPEN

    @hybrid_property
    def votes(self):
        return sum(choice.results.count() for choice in self.choices)

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
    poll = relationship(Poll, back_populates='poll')

    results = relationship("Result", back_populates='choice', cascade="all, delete, delete-orphan")


class Result(Base):
    """Table with users answers"""
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref='results')

    choice_id = Column(Integer, ForeignKey('choice.id'))
    choice = relationship(Choice, back_populates='results')


Base.metadata.create_all(engine)
