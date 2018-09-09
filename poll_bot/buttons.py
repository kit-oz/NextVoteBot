# -*- coding: utf-8 -*-

import html
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import RESULT_VISIBLE_MSG
from db.manager import DatabaseManager


def create_inline_menu(buttons):
    return InlineKeyboardMarkup([[InlineKeyboardButton(**btn) for btn in row] for row in buttons])


def get_admin_buttons(poll):
    """Basic poll administrator buttons"""
    buttons = [
        [{'text': 'Publish poll', 'switch_inline_query': '{}'.format(poll.id)}],
    ]

    if poll.votes == 0:
        buttons.append([{'text': 'Poll settings', 'callback_data': 'settings_{}'.format(poll.id)}])
    else:
        buttons.append([{'text': 'Update results', 'callback_data': 'update_{}'.format(poll.id)}])

    buttons.append([
        {'text': 'Close', 'callback_data': 'close_{}'.format(poll.id)},
        {'text': 'Delete', 'callback_data': 'delete_{}'.format(poll.id)},
    ])

    return create_inline_menu(buttons)


def get_answers_buttons(poll):
    """Buttons with answers to voting"""
    return create_inline_menu([
        [{'text': html.unescape(choice.text), 'callback_data': 'answer_{}_{}'.format(poll.id, choice.id)}]
        for choice in poll.choices
    ])


def confirm_delete_buttons(poll):
    """Delete confirmation dialog"""
    return create_inline_menu([
        [
            {'text': 'Yes', 'callback_data': 'del_{}'.format(poll.id)},
            {'text': 'No', 'callback_data': 'admin_{}'.format(poll.id)},
        ]
    ])


def poll_closed_buttons(poll):
    """Buttons shown when poll closed"""
    return create_inline_menu([
        [
            {'text': 'Open', 'callback_data': 'open_{}'.format(poll.id)},
            {'text': 'Delete', 'callback_data': 'delete_{}'.format(poll.id)},
        ]
    ])


def poll_settings_buttons(poll):
    """Poll settings menu"""
    can_change_answer = 'yes' if poll.can_change_answer else 'no'
    show_result = RESULT_VISIBLE_MSG[poll.result_visible]

    return create_inline_menu([
        [{
            'text': 'Show results: {}'.format(show_result),
            'callback_data': 'showresults_{}'.format(poll.id)
        }],
        [{
            'text': 'Can change answer: {}'.format(can_change_answer),
            'callback_data': 'changeanswer_{}'.format(poll.id)
        }],
        [{'text': 'Back to poll', 'callback_data': 'admin_{}'.format(poll.id)}],
    ])


def get_buttons_by_action(user, poll, action):
    user_can_vote = DatabaseManager.user_can_vote(user, poll)

    if action == 'answer' and not user_can_vote:
        return None

    poll_buttons = {
        'admin': get_admin_buttons,
        'answer': get_answers_buttons,
        'changeanswer': poll_settings_buttons,
        'close': poll_closed_buttons,
        'del': None,
        'delete': confirm_delete_buttons,
        'open': get_admin_buttons,
        'publish': None,
        'settings': poll_settings_buttons,
        'showresults': poll_settings_buttons,
    }
    return poll_buttons[action]
