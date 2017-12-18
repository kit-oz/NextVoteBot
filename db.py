# -*- coding: utf-8 -*-

import random
import string
from config import POLL_CODE_LENGTH
from model import Session
from model import User, Poll, Choice

session = Session()

unsaved_polls = {}


def get_user(user_id):
    user = session.query(User).get(user_id)
    if not user:
        user = User(id=user_id)
        session.add(user)
        session.commit()
    return user


def set_user_state(user, state):
    user.state = state
    session.add(user)
    session.commit()


def create_poll(author, raw_poll):
    if len(raw_poll['choices']) > 0:
        while True:
            new_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(POLL_CODE_LENGTH))
            poll_with_code = session.query(Poll).get(new_code)
            if not poll_with_code:
                break

        new_poll = Poll(id=new_code, author=author, question=raw_poll['question'])
        session.add(new_poll)

        for choice_text in raw_poll['choices']:
            choice = Choice(poll=new_poll, text=choice_text)
            session.add(choice)

        session.commit()

        return new_poll


def get_poll(poll_id):
    return session.query(Poll).get(poll_id)
