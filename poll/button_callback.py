# -*- coding: utf-8 -*-

from telegram import ParseMode
from telegram.error import BadRequest

from db.manager import DatabaseManager
from wrappers import load_user
from .buttons import poll_buttons
from .message import get_message_text


@load_user
def button_callback(bot, update, user):
    """Callback function when inline buttons are pressed"""
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
    poll = DatabaseManager.get_poll(params[1])

    if not poll:
        edit_message_args['reply_markup'] = ''
        # bot.editMessageReplyMarkup(**edit_message_args)
        bot.answerCallbackQuery(callback_query_id=query.id, text="Poll not found")
        return

    action = params[0]

    if action == 'answer':
        if poll.is_open:
            choice_id = params[2]
            vote_result = DatabaseManager.save_user_answer(user, poll, choice_id)
            bot.answerCallbackQuery(callback_query_id=query.id,
                                    text='You vote for {}. {}'.format(choice_id, vote_result))
        else:
            bot.answerCallbackQuery(callback_query_id=query.id,
                                    text="You can't vote for this poll")
    elif poll.author == user:
        if action == 'showresults':
            DatabaseManager.toggle_result_visibility(poll)
        elif action == 'changeanswer':
            DatabaseManager.toggle_can_change_answer(poll)
        elif action == 'close':
            DatabaseManager.close_poll(poll)
        elif action == 'open':
            DatabaseManager.open_poll(poll)
        elif action == 'del':
            DatabaseManager.delete_poll(poll)

    if poll.author != user:
        action = 'answer'

    buttons = poll_buttons[action]
    if buttons:
        edit_message_args['reply_markup'] = buttons(poll)

    edit_message_args['text'] = get_message_text(poll, user, action)

    try:
        bot.edit_message_text(**edit_message_args)
    except BadRequest:
        bot.answerCallbackQuery(callback_query_id=query.id, text='Shit happens')
