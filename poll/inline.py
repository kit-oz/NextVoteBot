# -*- coding: utf-8 -*-

import json
from uuid import uuid4

from telegram import ParseMode
from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent

from config import MESSAGES
from db.manager import DatabaseManager
from wrappers import load_user

from .buttons import poll_buttons
from .message import get_message_text


@load_user
def text_received(bot, update, user):
    """Save incoming text messages as poll template"""
    message_text = update.message.text
    poll_draft = DatabaseManager.get_poll_draft(user)
    if not poll_draft:
        DatabaseManager.create_poll(user=user, question=message_text)

        bot.send_message(
            chat_id=update.message.chat_id,
            text="Creating a new poll: '<b>{}</b>'\n\nPlease send me the first answer option.".format(message_text),
            parse_mode=ParseMode.HTML
        )
        return

    if len(poll_draft.choices) == 0:
        response_text = "Good. Now send me another answer option."
    else:
        response_text = "Good. Feel free to add more answer options.\n\nWhen you've added enough, " \
                        "simply send /done or press the button below to finish creating the poll."

    DatabaseManager.create_choice(poll=poll_draft, text=message_text)
    bot.send_message(chat_id=update.message.chat_id,
                     text=response_text)


@load_user
def inline_query(bot, update, user):
    """Inline search polls by ID or question text"""
    answer = {
        'results': [],
        'is_personal': True,
        'cache_time': 3
    }

    query = update.inline_query.query

    if query:
        poll_list = DatabaseManager.get_user_polls(user=user, query_text=query)
        for poll in poll_list:
            message_text = get_message_text(poll, user)
            buttons = poll_buttons['answer'](poll)
            answer['results'].append(
                InlineQueryResultArticle(
                    id=poll.id,
                    title=poll.question,
                    input_message_content=InputTextMessageContent(message_text=message_text,
                                                                  parse_mode=ParseMode.HTML),
                    reply_markup=buttons
                )
            )

    if len(answer['results']) == 0:
        answer['switch_pm_text'] = MESSAGES['CREATE_NEW_POLL']
        answer['switch_pm_parameter'] = '1'

    update.inline_query.answer(**answer)
