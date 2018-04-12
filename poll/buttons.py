# -*- coding: utf-8 -*-

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from db import db


def create_inline_menu(buttons):
    return InlineKeyboardMarkup([[InlineKeyboardButton(**btn) for btn in row] for row in buttons])


def main_control_buttons(poll):
    """Buttons for manage poll"""
    if poll.is_open():
        return create_inline_menu([
            [{'text': 'Publish poll', 'switch_inline_query': '{}'.format(poll.id)}],
            [{'text': 'Update results', 'callback_data': 'control_{}'.format(poll.id)}],
            [{'text': 'Poll settings', 'callback_data': 'settings_{}'.format(poll.id)}],
            [
                {'text': 'Close', 'callback_data': 'close_{}'.format(poll.id)},
                {'text': 'Delete', 'callback_data': 'delete_{}'.format(poll.id)},
            ]
        ])


def settings_buttons(poll):
    """Poll settings menu"""
    if poll.is_open():
        can_change_answer = 'yes' if poll.can_change_answer else 'no'
        return create_inline_menu([
            [{
                'text': 'Show results: {}'.format(Config.RESULT_VISIBLE_MSG[poll.result_visible]),
                'callback_data': 'showresults_{}'.format(poll.id)
            }],
            [{
                'text': 'Can change answer: {}'.format(can_change_answer),
                'callback_data': 'changeanswer_{}'.format(poll.id)
            }],
            [{'text': 'Back to poll', 'callback_data': 'control_{}'.format(poll.id)}],
        ])


def poll_closed_buttons(poll):
    if poll.is_closed():
        return create_inline_menu([
            [
                {'text': 'Open', 'callback_data': 'open_{}'.format(poll.id)},
                {'text': 'Delete', 'callback_data': 'delete_{}'.format(poll.id)},
            ]
        ])


def confirm_delete_buttons(poll):
    if not poll.is_deleted():
        return create_inline_menu([
            [
                {'text': 'Yes', 'callback_data': 'del_{}'.format(poll.id)},
                {'text': 'No', 'callback_data': 'control_{}'.format(poll.id)},
            ]
        ])


def answers_buttons(poll):
    if poll.is_open():
        choice_list = db.get_poll_choices(poll)
        return create_inline_menu(
            [[{'text': choice.text, 'callback_data': 'answer_{}_{}'.format(poll.id, choice.id)}]
             for choice in choice_list]
        )


poll_buttons = {
    'control': main_control_buttons,
    'settings': settings_buttons,
    'showresults': settings_buttons,
    'changeanswer': settings_buttons,
    'answer': answers_buttons,
    'close': poll_closed_buttons,
    'open': main_control_buttons,
    'delete': confirm_delete_buttons,
    'del': None,
    'publish': None
}
