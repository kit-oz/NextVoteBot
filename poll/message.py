# -*- coding: utf-8 -*-

from config import POLL_CLOSED
from db import db


def get_message_text(poll, user, action=''):
    message_text = [
        '<b>{}</b>'.format(poll.question),
    ]

    poll_results = db.get_poll_results(poll)

    show_result = db.check_show_poll_results(poll, user, action)
    if show_result:
        poll_results = sorted(poll_results, key=lambda x: x['result_count'], reverse=True)

    max_result = max(poll_result['result_count'] for poll_result in poll_results)
    total_results = sum(poll_result['result_count'] for poll_result in poll_results)

    choices = []
    for choice in poll_results:
        choice_label = choice['text']
        choice_result = choice['result_count']
        choice_percent = 0 if total_results == 0 else 100 * choice_result / total_results
        if show_result:
            choice_label += ' - {}\n{}%'.format(
                choice_result,
                '{:.0f}'.format(choice_percent)
            )
        choices.append(choice_label)

    message_text.append('\n\n'.join([choice_label for choice_label in choices]))

    if total_results == 0:
        footer = '👥 Nobody voted so far.'
    elif total_results == 1:
        footer = '👥 1 person voted so far.'
    else:
        footer = '👥 {} people voted so far.'.format(total_results)
    message_text.append(footer)

    if poll.state == POLL_CLOSED:
        message_text[2] += ' <i>Poll closed.</i>'

    if action == 'delete':
        message_text[2] += '\n\n<b>Deleting a poll with permanently remove it from your inline suggestions and bot settings. It will appear closed to all other users.\n\nDelete poll?</b>'

    return '\n\n'.join(message_text)
