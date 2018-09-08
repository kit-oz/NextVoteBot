# -*- coding: utf-8 -*-

import html
from telegram import ParseMode
from telegram.error import BadRequest

from db.manager import DatabaseManager
from wrappers import load_user
from .buttons import get_buttons_by_action
from .message import get_message_text


def vote_for_poll(bot, update, user, poll, choice_id):
    """"""
    save_success = False

    choice = DatabaseManager.get_choice(choice_id)
    user_choice = DatabaseManager.get_user_choice(user=user, poll=poll)

    if choice.poll_id != poll.id:
        save_success = False
    elif not poll.is_open and not poll.is_unpublished:
        save_success = True
        callback_text = "You can't vote. Poll is closed"
    elif not user_choice:
        save_success = DatabaseManager.save_user_choice(poll, user, choice)
        callback_text = "You vote for ..."
    elif not poll.can_change_answer:
        callback_text = "You can't change answer"
    elif user_choice.id == choice.id:
        save_success = DatabaseManager.delete_user_choice(user_choice)
        callback_text = "You took your answer"
    else:
        save_success = DatabaseManager.update_user_answer(user_choice, choice)
        callback_text = "You change your answer to ..."

    if save_success:
        callback_text = 'An error was occured. Try again'

        if poll.is_unpublished:
            DatabaseManager.open_poll(poll)

    bot.answerCallbackQuery(callback_query_id=update.callback_query.id,
                            text=callback_text)


def update_poll_settings(poll, action):
    if action == 'showresults' and poll.is_unpublished:
        DatabaseManager.toggle_result_visibility(poll)
    elif action == 'changeanswer' and poll.is_unpublished:
        DatabaseManager.toggle_can_change_answer(poll)
    elif action == 'close':
        DatabaseManager.close_poll(poll)
    elif action == 'open':
        DatabaseManager.open_poll(poll)
    elif action == 'del':
        DatabaseManager.delete_poll(poll)


def update_poll_message(bot, update, user, poll, action):
    edit_message_args = {
        'parse_mode': ParseMode.HTML
    }

    query = update.callback_query
    if query.message:
        edit_message_args['chat_id'] = query.message.chat.id
        edit_message_args['message_id'] = query.message.message_id
    else:
        edit_message_args['inline_message_id'] = query.inline_message_id

    if poll.author != user:
        action = 'answer'
    elif poll.is_open and action in ('settings', 'changeanswer', 'showresults'):
        action = 'admin'
    elif poll.is_closed and action == 'admin':
        action = 'close'
    elif poll.is_deleted:
        action = 'del'

    buttons = get_buttons_by_action(action)
    if buttons:
        edit_message_args['reply_markup'] = buttons(poll)

    edit_message_args['text'] = get_message_text(poll, user, action=action)

    try:
        bot.edit_message_text(**edit_message_args)
    except BadRequest:
        bot.answerCallbackQuery(callback_query_id=query.id, text='Shit happens')


@load_user
def button_callback(bot, update, user):
    """Callback function when inline buttons are pressed"""
    query = update.callback_query
    query_data = html.escape(query.data).split('_')

    poll_id = query_data[1]
    poll = DatabaseManager.get_poll(poll_id)
    if not poll:
        bot.answerCallbackQuery(callback_query_id=query.id, text="Poll not found")
        return

    action = query_data[0]
    if action == 'answer':
        choice_id = query_data[2]
        vote_for_poll(bot, update, user, poll, choice_id)
    elif poll.author == user:
        update_poll_settings(poll, action)

    update_poll_message(bot, update, user, poll, action)
