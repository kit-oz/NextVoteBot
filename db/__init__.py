# -*- coding: utf-8 -*-

from __future__ import absolute_import
import random
import string
from sqlalchemy import or_, func
from config import INLINE_SEARCH_RESULTS, VISIBLE_ALWAYS, VISIBLE_AFTER_ANSWER
from config import POLL_CODE_LENGTH, POLL_OPEN, POLL_DELETED
from .model import Session
from .model import User, Poll, Choice, Result


class Database(object):
    def __init__(self):
        self.session = Session()
        self.poll_templates = {}

    def get_user_by_id(self, from_user):
        if not from_user.is_bot:
            user_id = from_user.id
            user = self.session.query(User).get(user_id)
            if not user:
                user = User(id=user_id)
                self.session.add(user)
                self.session.commit()
            return user

    def set_user_state(self, user, state):
        user.state = state
        self.session.add(user)
        self.session.commit()

    def get_user_polls(self, user, count=INLINE_SEARCH_RESULTS, page=0, with_closed=False):
        offset = page * count

        query = self.session.query(
            Poll.id,
            Poll.question,
            Poll.date,
            func.count(Result.id).label('result_count')
        )
        query = query.outerjoin(Result)
        query = query.filter(Poll.user_id == user.id)

        if with_closed:
            query = query.filter(Poll.state != POLL_DELETED)
        else:
            query = query.filter(Poll.state == POLL_OPEN)

        query = query.group_by(Poll.id)
        query = query.offset(offset).limit(count)

        return query.all()

    def get_user_choice(self, user, poll):
        return self.session.query(Result).filter(Result.poll_id == poll.id,
                                                 Result.user_id == user.id).first()

    def create_poll(self, user):
        if user.id in self.poll_templates:
            poll_template = self.poll_templates[user.id]
            if len(poll_template['choices']) > 0:
                while True:
                    new_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(POLL_CODE_LENGTH))
                    poll_with_code = self.session.query(Poll).get(new_code)
                    if not poll_with_code:
                        break

                new_poll = Poll(id=new_code, user=user, question=poll_template['question'])
                self.session.add(new_poll)

                for choice_text in poll_template['choices']:
                    choice = Choice(poll=new_poll, text=choice_text)
                    self.session.add(choice)

                self.session.commit()

                del self.poll_templates[user.id]

                return new_poll

    def get_poll_by_id(self, poll_id):
        return self.session.query(Poll).get(poll_id)

    def search_poll(self, user, query_text, count=INLINE_SEARCH_RESULTS):
        return self.session.query(Poll).filter(
            Poll.user_id == user.id,
            or_(
                Poll.question.ilike('%{}%'.format(query_text)),
                Poll.id.like('%{}%'.format(query_text))
            )
        ).order_by(Poll.date.desc()).limit(count).all()

    def set_poll_state(self, poll, state):
        poll.state = state
        self.session.add(poll)
        self.session.commit()

    def toggle_result_visibility(self, poll):
        poll.result_visible = 0 if poll.result_visible == 2 else poll.result_visible + 1
        self.session.add(poll)
        self.session.commit()

    def toggle_can_change_answer(self, poll):
        poll.can_change_answer = not poll.can_change_answer
        self.session.add(poll)
        self.session.commit()

    def get_poll_results(self, poll):
        query_results = self.session.query(
            Choice.text,
            func.count(Result.id).label('result_count')
        ).outerjoin(
            Result
        ).filter(
            Choice.poll_id == poll.id
        ).group_by(
            Choice.id
        ).all()

        poll_results = []
        for query_result in query_results:
            poll_results.append({'text': query_result.text, 'result_count': query_result.result_count})
        return poll_results

    def get_poll_choices(self, poll):
        return self.session.query(Choice).filter(Choice.poll_id == poll.id).all()

    def save_user_answer(self, user, poll, choice_id):
        choice = self.session.query(Choice).get(choice_id)
        if choice.poll_id == poll.id:
            result = self.session.query(Result).filter(Result.user_id == user.id,
                                                       Result.poll_id == poll.id).first()
            if not result:
                result = Result(user=user, poll=poll, choice=choice)
                self.session.add(result)
            else:
                if result.choice_id == choice_id:
                    self.session.delete(result)
                else:
                    result.choice = choice
                    self.session.add(result)
            self.session.commit()

    def check_show_poll_results(self, poll, user, action=''):
        if poll.result_visible == VISIBLE_ALWAYS:
            return True

        if user.is_author(poll) and action != 'answer':
            return True

        user_choice = self.get_user_choice(user=user, poll=poll)
        if user_choice and poll.result_visible == VISIBLE_AFTER_ANSWER:
            return True

        return False


db = Database()
