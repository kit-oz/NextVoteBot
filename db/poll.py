# -*- coding: utf-8 -*-

import random
import string

from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from .common import db
from .choice import Choice


class Poll(db.Model):
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

    id = db.Column(db.String(CODE_LENGTH), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    question = db.Column(db.String(250))

    state = db.Column(db.Integer, default=DRAFT)
    result_visible = db.Column(db.Integer, default=RESULT_VISIBLE_AFTER_ANSWER)
    can_change_answer = db.Column(db.Boolean, default=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    choices = db.relationship(Choice, backref='poll', cascade="delete, delete-orphan")

    def __init__(self, author, question):
        while True:
            new_code = ''.join(random.choice(string.ascii_letters + string.digits)
                               for _ in range(self.CODE_LENGTH))
            poll_with_code = db.query(Poll).get(new_code)
            if not poll_with_code:
                break

        self.id = new_code
        self.author_id = author.id
        self.question = question

    @hybrid_property
    def is_open(self):
        return self.state == self.OPEN

    @hybrid_property
    def is_closed(self):
        return self.state == self.CLOSED

    @hybrid_property
    def is_deleted(self):
        return self.state == self.DELETED

    @hybrid_property
    def votes(self):
        return sum(choice.votes for choice in self.choices)
