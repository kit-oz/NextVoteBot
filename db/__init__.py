# -*- coding: utf-8 -*-

from __future__ import absolute_import

from sqlalchemy import or_
from sqlalchemy import func

from .model import Choice
from .model import Poll
from .model import Result
from .model import Session
from .model import User


class Database(object):
    def __init__(self):
        self.session = Session()

    def create_choice(self, poll, text):
        """Create new choice for poll

        Args:
            poll: instance of a class User
            text: choice text

        Returns:
            choice: instance of a class Choice
        """
        choice = Choice(poll=poll, text=text)
        self.session.add(choice)
        self.session.commit()

        return choice

    def create_poll(self, user, question):
        """Create new poll

        Args:
            user: instance of a class User
            question: question text

        Returns:
            poll: instance of a class Poll
        """
        poll = Poll(user=user, question=question)
        self.session.add(poll)
        self.session.commit()

        return poll

    def delete_draft_poll(self, user):
        """Delete unfinished poll

        Args:
            user: instance of a class User

        Returns:
            None
        """
        poll_draft = db.get_poll_draft(user)
        if poll_draft:
            self.session.delete(poll_draft)
            self.session.commit()

    def get_user(self, user_id):
        """Get user by his Telegram ID

        Create new user if no one found

        Args:
            user_id: Telegram User ID
        """
        user = self.session.query(User).get(user_id)
        if not user:
            user = User(id=user_id)
            self.session.add(user)
            self.session.commit()
        return user

    def get_user_choice(self, user, poll):
        """Get user choice for current poll

        Args:
            user: instance of a class User
            poll: instance of a class Poll

        Returns:
            result: instance of a class Result
        """
        choice, result = self.session.query(Choice, Result).\
            filter(Choice.id == Result.choice_id).\
            filter(Choice.poll_id == poll.id).\
            filter(Result.user_id == user.id).\
            all()

        return choice

    def get_poll(self, poll_id):
        """Get poll by ID

        Args:
            poll_id: poll ID

        Returns:
            poll: instance of a class Poll
        """
        return self.session.query(Poll).get(poll_id)

    def get_poll_draft(self, user):
        """Get poll draft of this user

        Args:
            user: instance of a class User

        Returns:
            poll: instance of a class Poll
        """
        return self.session.query(Poll).filter(Poll.user_id == user.id, Poll.is_draft).first()






    def get_user_polls(self, user, count=5, page=0, with_closed=False):
        """Get an array of polls from the current user

        Args:
            user: instance of a class User
            count: polls count per page
            page: page number
            with_closed: include closed polls or not

        Returns:
            Array of instances of a class Poll
        """
        offset = page * count

        query = self.session.query(
            Poll.id,
            Poll.question,
            Poll.date,
            func.count(Result.id).label('result_count')
        )
        query = query.outerjoin(Result)
        query = query.filter(Poll.user_id == user.id)
        query = query.filter(Poll.state != Poll.DRAFT)

        if with_closed:
            query = query.filter(Poll.state != Poll.DELETED)
        else:
            query = query.filter(Poll.state == Poll.OPEN)

        query = query.group_by(Poll.id)
        query = query.offset(offset).limit(count)

        return query.all()

    def search_poll(self, user, query_text, count=5):
        """Search poll by its ID or question text

        Args:
            user: instance of a class User
            query_text: poll ID or text from poll question
            count: polls count for return

        Returns:
            An array of instances of a class Poll
        """
        return self.session.query(Poll).filter(
            Poll.user_id == user.id,
            or_(
                Poll.question.ilike('%{}%'.format(query_text)),
                Poll.id.like('%{}%'.format(query_text))
            )
        ).order_by(Poll.date.desc()).limit(count).all()

    def set_poll_state(self, poll, state):
        """Change state for the poll

        Args:
            poll: instance of a class Poll
            state: poll state for write

        Returns:
            None
        """
        poll.state = state
        self.session.add(poll)
        self.session.commit()

    def toggle_result_visibility(self, poll):
        """Change the visibility of results

        Args:
            poll: instance of a class Poll

        Returns:
            None
        """
        poll.result_visible = 0 if poll.result_visible == 2 else poll.result_visible + 1
        self.session.add(poll)
        self.session.commit()

    def toggle_can_change_answer(self, poll):
        """Change the ability to change the answer

        Args:
            poll: instance of a class Poll

        Returns:
            None
        """
        poll.can_change_answer = not poll.can_change_answer
        self.session.add(poll)
        self.session.commit()

    # TODO Add save result return
    def save_user_answer(self, user, poll, choice_id):
        """Verify that the user can vote and save his response

        Args:
            user: instance of a class User
            poll: instance of a class Poll
            choice_id: ID of the selected answer

        Returns:
            None
        """
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
        """Check can user view poll results

        Args:
            poll: instance of a class User
            user: instance of a class User
            action: current user action

        Returns:
            True if user can view poll result, else False
        """
        if poll.is_result_visible_always():
            return True

        # if poll.author == user and action != 'answer':
        #     return True

        user_choice = self.get_user_choice(user=user, poll=poll)
        if user_choice and poll.is_result_visible_after_answer():
            return True

        return False


db = Database()
