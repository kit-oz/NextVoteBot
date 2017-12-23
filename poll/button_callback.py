# -*- coding: utf-8 -*-

from db.middleware import db
from config import POLL_OPEN, POLL_CLOSED, POLL_DELETED
from .buttons import poll_buttons
from .message import get_message_text


def button_callback(bot, update):
    query = update.callback_query
    print(query)
    user = db.get_user_by_id(query.from_user.id)

    params = query.data.split('_')
    poll = db.get_poll_by_id(params[1])

    if poll and poll.state != POLL_DELETED:
        action = params[0]

        if action == 'showresults':
            db.toggle_result_visibility(poll)
        elif action == 'changeanswer':
            db.toggle_can_change_answer(poll)
        elif action == 'close':
            db.set_poll_state(poll, POLL_CLOSED)
        elif action == 'open':
            db.set_poll_state(poll, POLL_OPEN)
        elif action == 'del':
            db.set_poll_state(poll, POLL_DELETED)
        elif action == 'answer':
            choice_id = params[2]
            db.save_user_answer(user, poll, choice_id)

        buttons = poll_buttons[action](poll)
        message_text = get_message_text(poll, user, action)
        if buttons:
            bot.edit_message_text(chat_id=query.chat_instance,
                                  message_id=query.inline_message_id,
                                  text=message_text,
                                  reply_markup=buttons)
        else:
            bot.edit_message_text(chat_id=query.chat_instance,
                                  message_id=query.inline_message_id,
                                  text=message_text)
