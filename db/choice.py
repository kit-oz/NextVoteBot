# -*- coding: utf-8 -*-

from .common import db
from .result import Result


class Choice(db.Model):
    """Table with answers to polls"""
    __tablename__ = 'choice'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))

    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))

    results = db.relationship(Result, backref='choice', cascade="delete, delete-orphan")
