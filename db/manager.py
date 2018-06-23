# -*- coding: utf-8 -*-

from __future__ import absolute_import

from sqlalchemy import or_

from .common import db
from .choice import Choice
from .poll import Poll
from .result import Result
from .user import User


class DatabaseManager:
    @staticmethod
    def check_result_visible(poll, user):
        """Check can user view poll results

        Args:
            poll: instance of a class User
            user: instance of a class User

        Returns:
            True if user can view poll result, else False
        """
        if poll.result_visible == Poll.RESULT_VISIBLE_ALWAYS:
            return True

        if poll.result_visible == Poll.RESULT_VISIBLE_NEVER:
            return False

        user_choice = DatabaseManager.get_user_choice(user=user, poll=poll)

        if user_choice:
            return True

        return False

    @staticmethod
    def close_poll(poll):
        """Change state for the poll to closed

        Args:
            poll: instance of a class Poll

        Returns:
            None
        """
        poll.state = Poll.CLOSED
        db.add(poll)
        db.commit()

    @staticmethod
    def create_choice(poll, text):
        """Create new choice for poll

        Args:
            poll: instance of a class User
            text: choice text

        Returns:
            choice: instance of a class Choice
        """
        choice = Choice(poll=poll, text=text)
        db.add(choice)
        db.commit()

        return choice

    @staticmethod
    def create_poll(user, question):
        """Create new poll

        Args:
            user: instance of a class User
            question: question text

        Returns:
            poll: instance of a class Poll
        """
        poll = Poll(author=user, question=question)
        db.add(poll)
        db.commit()

        return poll

    @staticmethod
    def delete_draft_poll(user):
        """Delete unfinished poll

        Args:
            user: instance of a class User

        Returns:
            None
        """
        db.query(Poll).filter_by(author_id=user.id, state=Poll.DRAFT).delete()

    @staticmethod
    def delete_poll(poll):
        """Change state for the poll to deleted

        Args:
            poll: instance of a class Poll

        Returns:
            None
        """
        poll.state = Poll.DELETED
        db.add(poll)
        db.commit()

    @staticmethod
    def get_choices_count():
        """Get total count of created choices to created polls"""
        choices_count = db.query(Choice) \
            .join(Choice.poll) \
            .filter(Poll.state > Poll.DRAFT) \
            .count()
        return choices_count

    @staticmethod
    def get_created_polls_count():
        """Get total count of created polls"""
        polls_created = db.query(Poll).filter(Poll.state > Poll.DRAFT).count()
        return polls_created

    @staticmethod
    def get_poll(poll_id):
        """Get poll by ID

        Args:
            poll_id: poll ID

        Returns:
            poll: instance of a class Poll
        """
        return db.query(Poll).get(poll_id)

    @staticmethod
    def get_poll_draft(author):
        """Get poll draft of this user

        Args:
            author: instance of a class User

        Returns:
            poll: instance of a class Poll
        """
        poll_draft = db.query(Poll).filter_by(author_id=author.id, state=Poll.DRAFT).first()
        return poll_draft

    @staticmethod
    def get_results_count():
        """Get total count of created polls"""
        results_count = db.query(Result).count()
        return results_count

    @staticmethod
    def get_user(user_id, user_name=''):
        """Get user by his Telegram ID

        Create new user if no one found

        Args:
            user_id: Telegram User's ID
            user_name: Telegram User‘s username
        """
        user = db.query(User).get(user_id)
        if not user:
            user = User(id=user_id, name=user_name)
            db.add(user)
            db.commit()
        return user

    @staticmethod
    def get_user_choice(user, poll):
        """Get user choice for current poll

        Args:
            user: instance of a class User
            poll: instance of a class Poll

        Returns:
            result: instance of a class Result
        """
        choice = db.query(Choice) \
            .join(Choice.results) \
            .filter(Choice.poll_id == poll.id) \
            .filter(Result.user_id == user.id) \
            .all()

        return choice

    @staticmethod
    def get_user_polls(user, page=1, per_page=5, with_closed=False, query_text=''):
        """Get an array of polls from the current user

        Args:
            user: instance of a class User
            page: page number
            per_page: polls count per page
            with_closed: include closed polls or not
            query_text: poll ID or text from poll question

        Returns:
            Array of instances of a class Poll
        """
        query = db.query(Poll) \
            .filter(Poll.author_id == user.id) \
            .filter(Poll.state != Poll.DRAFT)

        if with_closed:
            query = query.filter(Poll.state != Poll.DELETED)
        else:
            query = query.filter(Poll.state == Poll.OPEN)

        if query_text:
            query = query.filter(or_(
                Poll.question.ilike('%{}%'.format(query_text)),
                Poll.id.like('{}'.format(query_text))
            ))

        query = query.paginate(page=page, per_page=per_page)

        return query

    @staticmethod
    def get_authors_count():
        """Get total count of users with polls created"""
        authors_count = db.query(Poll.author_id).group_by(Poll.author_id).count()
        return authors_count

    @staticmethod
    def open_poll(poll):
        """Change state for the poll to open

        Args:
            poll: instance of a class Poll

        Returns:
            None
        """
        poll.state = Poll.OPEN
        db.add(poll)
        db.commit()

    @staticmethod
    def save_user_answer(user, poll, choice_id):
        """Verify that the user can vote and save his response

        Args:
            user: instance of a class User
            poll: instance of a class Poll
            choice_id: ID of the selected answer

        Returns:
            Vote result
        """
        choice = db.query(Choice).get(choice_id)
        if choice.poll_id != poll.id:
            return 'error'

        result = db.query(Result).join(Result.choice) \
            .filter(Result.user_id == user.id) \
            .filter(Choice.poll_id == poll.id) \
            .first()

        if not result:
            result = Result(user=user, choice=choice)
            db.add(result)
            db.commit()
            return 'vote'

        if result.choice == choice:
            db.delete(result)
            db.commit()
            return 'took'

        result.choice = choice
        db.add(result)
        db.commit()
        return 'change'

    @staticmethod
    def toggle_can_change_answer(poll):
        """Change the ability to change the answer

        Args:
            poll: instance of a class Poll

        Returns:
            None
        """
        poll.can_change_answer = not poll.can_change_answer
        db.add(poll)
        db.commit()

    @staticmethod
    def toggle_result_visibility(poll):
        """Change the visibility of results

        Args:
            poll: instance of a class Poll

        Returns:
            None
        """
        poll.result_visible = 0 if poll.result_visible == 2 else poll.result_visible + 1
        db.add(poll)
        db.commit()
