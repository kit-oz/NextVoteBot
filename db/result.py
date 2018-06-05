# -*- coding: utf-8 -*-

from datetime import datetime

from .common import db


class Result(db.Model):
    """Table with users answers"""
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    choice_id = db.Column(db.Integer, db.ForeignKey('choice.id'))
