# -*- coding: utf-8 -*-

from telegram import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from model import Choice, Result
from db import session, get_user, get_poll


def create_inline_menu(buttons):
    return InlineKeyboardMarkup([[InlineKeyboardButton(**btn) for btn in row] for row in buttons])


def get_admin_buttons(poll):
    return create_inline_menu([
        [{'text': 'Publish poll', 'callback_data': 'publish_{}'.format(poll.id)}],
        [{'text': 'Update results', 'callback_data': 'update_{}'.format(poll.id)}],
        [{'text': 'Poll settings', 'callback_data': 'settings_{}'.format(poll.id)}],
        [
            {'text': 'Vote', 'callback_data': 'vote_{}'.format(poll.id)},
            {'text': 'Close', 'callback_data': 'close_{}'.format(poll.id)},
            {'text': 'Delete', 'callback_data': 'delete_{}'.format(poll.id)},
        ]
    ])


def get_settings_buttons(poll):
    result_visible = ['never', 'after answer', 'always']
    can_change_answer = 'yes' if poll.can_change_answer else 'no'
    return create_inline_menu([
        [{
            'text': 'Results visible: {}'.format(result_visible[poll.result_visible]),
            'callback_data': 'visibility_{}'.format(poll.id)
        }],
        [{
            'text': 'Can change answer: {}'.format(can_change_answer),
            'callback_data': 'change_{}'.format(poll.id)
        }],
        [{'text': 'Back to poll', 'callback_data': 'admin_{}'.format(poll.id)}],
    ])


def get_close_buttons(poll):
    return create_inline_menu([
        [
            {'text': 'Open', 'callback_data': 'open_{}'.format(poll.id)},
            {'text': 'Delete', 'callback_data': 'delete_{}'.format(poll.id)},
        ]
    ])


def get_confirm_delete_buttons(poll):
    return create_inline_menu([
        [
            {'text': 'Yes', 'callback_data': 'del_{}'.format(poll.id)},
            {'text': 'No', 'callback_data': 'admin_{}'.format(poll.id)},
        ]
    ])


def get_choices(poll):
    choice_list = session.query(Choice).filter(Choice.poll_id == poll.id).all()
    return create_inline_menu(
        [{'text': choice.text, 'callback_data': 'answer_{}_{}'.format(poll.id, choice.id)} for choice in choice_list]
    )


def get_message_text(poll):
    choice_list = session.query(Choice).filter(Choice.poll_id == poll.id).all()
    result_list = session.query(Result).filter(Result.poll_id == poll.id).all()
    message_text = "*{question}*\n\n{answers}\n\n👥 Nobody voted so far.".format(
        question=poll.text,
        answers='\n\n'.join([choice.text for choice in choice_list])
    )
    return message_text


def send_poll_settings(bot, update, poll):
    bot.send_message(chat_id=update.message.chat_id,
                     text=get_message_text(poll),
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=get_admin_buttons(poll))


def button_callback(bot, update):
    query = update.callback_query
    user = get_user(query.message.from_user.id)

    params = query.data.split('_')
    poll = get_poll(params[1])

    if poll:
        action = params[0]
        bot.edit_message_text(text=get_message_text(poll),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
