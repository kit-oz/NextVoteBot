# -*- coding: utf-8 -*-

from config import MESSAGES
from db.manager import DatabaseManager


def get_chart(poll, user, action):
    show_result = True if action != 'answer' else DatabaseManager.check_result_visible(poll, user)

    choice_template = '{state} {text} - {votes}\n{likes} {percent:.0f}%' if show_result else '{state} {text}'

    max_votes = max(choice.votes for choice in poll.choices)
    choices = [{
        'text': choice.text,
        'votes': choice.votes,
        'user_choice': choice.is_user_choice(user),
        'likes': 0 if max_votes == 0 else round(len(choice.results) / max_votes) * 12,
        'percent': 0 if poll.votes == 0 else 100 * len(choice.results) / poll.votes
    } for choice in poll.choices]

    if show_result:
        choices = sorted(choices, key=lambda x: x['votes'], reverse=True)

    result = [choice_template.format(
        state='&#9635;' if choice['user_choice'] else '&#9633;',
        text=choice['text'],
        votes=choice['votes'],
        likes='&#124;' if choice['likes'] == 0 else '&#9632;️' * choice['likes'],
        # likes='&#9643;' if choice['likes'] == 0 else '&#128077;️' * choice['likes'],
        percent=choice['percent']
    ) for choice in choices]

    return '\n'.join(result)


def get_total_votes(poll):
    """"""
    if poll.votes == 0:
        return MESSAGES['POLL_FOOTER_NO_VOTES']
    elif poll.votes == 1:
        return MESSAGES['POLL_FOOTER_ONE_VOTE']
    else:
        return MESSAGES['POLL_FOOTER_VOTES'].format(votes=poll.votes)


def get_message_text(poll, user, action='answer'):
    """Build poll text"""
    message_text = []

    poll_title = '<b>{}</b>'.format(poll.question)
    chart = get_chart(poll, user, action)
    total_votes = get_total_votes(poll)
    user_can_vote = DatabaseManager.user_can_vote(user, poll)

    message_text.append(poll_title)
    message_text.append(chart)
    message_text.append(total_votes)

    if action == 'delete':
        message_text.append(MESSAGES['POLL_DELETE_ALERT'])
    elif action == 'admin' and poll.votes == 0:
        message_text.append(MESSAGES['PUBLICATION_WARNING'])
    elif poll.is_closed or poll.is_deleted:
        message_text.append(MESSAGES['POLL_FOOTER_CLOSED'])
    elif action == 'answer' and not poll.can_change_answer and user_can_vote:
        message_text.append(MESSAGES['CANT_CHANGE_ANSWER'])

    return '\n\n'.join(message_text)
