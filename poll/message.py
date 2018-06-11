# -*- coding: utf-8 -*-

from config import MESSAGES
from db.manager import DatabaseManager


def get_chart(poll, user, show_result=True):
    if show_result:
        max_votes = max(len(choice.results) for choice in poll.choices)

        choices = [{
            'text': choice.text,
            'votes': len(choice.results),
            'user_choice': choice.is_user_choice(user),
            'likes': 0 if max_votes == 0 else round(len(choice.results)/max_votes) * 7,
            'percent': 0 if poll.votes == 0 else 100 * len(choice.results) / poll.votes
        } for choice in poll.choices]
        choices = sorted(choices, key=lambda x: x['votes'], reverse=True)

        result = ['{text} - {votes}{user_choice}\n{likes} {percent:.0f}%'.format(
            text=choice['text'],
            votes=choice['votes'],
            user_choice=' (your choice)' if choice['user_choice'] else '',
            likes='▫' if choice['likes'] == 0 else '👍️' * choice['likes'],
            percent=choice['percent']
        ) for choice in choices]
    else:
        result = ['{text}{user_choice}'.format(
            text=choice.text,
            user_choice=' (your choice)' if choice.is_user_choice(user) else ''
        ) for choice in poll.choices]

    return '\n\n'.join(result)


def get_message_text(poll, user, action=''):
    """Build poll text"""
    message_text = [
        '<b>{}</b>'.format(poll.question),
    ]

    show_result = DatabaseManager.check_result_visible(poll, user)

    chart = get_chart(poll, user, show_result)
    message_text.append(chart)

    footer = []
    if poll.votes == 0:
        footer.append(MESSAGES['POLL_FOOTER_NO_VOTES'])
    elif poll.votes == 1:
        footer.append(MESSAGES['POLL_FOOTER_ONE_VOTE'])
    else:
        footer.append(MESSAGES['POLL_FOOTER_VOTES'].format(votes=poll.votes))

    if not poll.is_open:
        footer.append(MESSAGES['POLL_FOOTER_CLOSED'])
    message_text.append(' '.join(footer))

    if action == 'delete':
        message_text.append(MESSAGES['POLL_DELETE_ALERT'])

    return '\n\n'.join(message_text)
