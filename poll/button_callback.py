# -*- coding: utf-8 -*-

from telegram import ParseMode
from telegram.error import BadRequest

from db import db
from wrappers import load_user
from .buttons import poll_buttons
from .message import get_message_text


@load_user
def button_callback(bot, update, user):
    edit_message_args = {
        'parse_mode': ParseMode.HTML
    }

    query = update.callback_query
    if query.message:
        edit_message_args['chat_id'] = query.message.chat.id
        edit_message_args['message_id'] = query.message.message_id
    else:
        edit_message_args['inline_message_id'] = query.inline_message_id

    params = query.data.split('_')
    poll = db.get_poll_by_id(params[1])

    if not poll:
        edit_message_args['reply_markup'] = ''
        bot.editMessageReplyMarkup(**edit_message_args)
    else:
        action = params[0]

        if action == 'answer' and poll.is_open():
            choice_id = params[2]
            db.save_user_answer(user, poll, choice_id)
            bot.answerCallbackQuery(callback_query_id=query.id, text='You vote for {}'.format(choice_id))
        elif user.is_author(poll):
            if action == 'showresults':
                db.toggle_result_visibility(poll)
            elif action == 'changeanswer':
                db.toggle_can_change_answer(poll)
            elif action == 'close':
                db.set_poll_state(poll, poll.CLOSED)
            elif action == 'open':
                db.set_poll_state(poll, poll.OPEN)
            elif action == 'del':
                db.set_poll_state(poll, poll.DELETED)

        if not poll.is_deleted():
            action = 'del'
        elif not user.is_author(poll):
            action = 'answer'

        buttons = poll_buttons[action]
        if buttons:
            edit_message_args['reply_markup'] = buttons(poll)

        edit_message_args['text'] = get_message_text(poll, user, action)

        try:
            bot.edit_message_text(**edit_message_args)
        except BadRequest:
            bot.answerCallbackQuery(callback_query_id=query.id, text='Shit happens')
