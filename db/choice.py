# -*- coding: utf-8 -*-

from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.ext.hybrid import hybrid_property

from .common import db
from .result import Result


class Choice(db.Model):
    """Table with answers to polls"""
    __tablename__ = 'choice'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))

    poll_id = db.Column(db.String, db.ForeignKey('poll.id'), index=True)

    results = db.relationship(Result, backref='choice', cascade="delete, delete-orphan")

    @hybrid_method
    def is_user_choice(self, user):
        user_results = db.query(Result).filter_by(choice_id=self.id, user_id=user.id).count()
        return user_results > 0

    @hybrid_property
    def votes(self):
        return len(self.results)
