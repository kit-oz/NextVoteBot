# -*- coding: utf-8 -*-

from db import db


def get_message_text(poll, user, action=''):
    """Build poll text"""
    message_text = [
        '<b>{}</b>'.format(poll.question),
    ]

    poll_results = db.get_poll_results(poll)

    show_result = db.check_show_poll_results(poll, user, action)
    if show_result:
        poll_results = sorted(poll_results, key=lambda x: x['result_count'], reverse=True)

    # max_result = max(poll_result['result_count'] for poll_result in poll_results)
    total_results = sum(poll_result['result_count'] for poll_result in poll_results)

    choices = []
    for choice in poll_results:
        if show_result:
            # TODO add emoticons as a chart
            choice_result = choice['result_count']
            choice_percent = 0 if total_results == 0 else 100 * choice_result / total_results
            choices.append('{} - {}\n{}%'.format(choice['text'], choice_result, '{:.0f}'.format(choice_percent)))
        else:
            choices.append(choice['text'])

    message_text.append('\n\n'.join(choices))

    footer = []
    if total_results == 0:
        footer.append('👥 Nobody voted so far.')
    elif total_results == 1:
        footer.append('👥 1 person voted so far.')
    else:
        footer.append('👥 {} people voted so far.'.format(total_results))

    if poll.is_closed():
        footer.append(' <i>Poll closed.</i>')
    message_text.append(''.join(footer))

    if action == 'delete':
        message_text.append('\n<b>Deleting a poll with permanently remove it from your inline suggestions '
                            'and bot settings. It will appear closed to all other users.\n\nDelete poll?</b>')

    return '\n\n'.join(message_text)
