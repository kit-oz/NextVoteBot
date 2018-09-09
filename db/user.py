# -*- coding: utf-8 -*-

from sqlalchemy.ext.hybrid import hybrid_property

from .common import db
from .poll import Poll
from .result import Result


class User(db.Model):
    """Table with users"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)
    # language_code = db.Column(db.String)

    polls = db.relationship(Poll, backref='author', cascade="delete, delete-orphan")
    votes = db.relationship(Result, backref='user')

    @hybrid_property
    def opened_polls(self):
        return [poll for poll in self.polls if poll.is_open]

    @hybrid_property
    def closed_polls(self):
        return [poll for poll in self.polls if poll.is_closed]
