# -*- coding: utf-8 -*-

from telegram import ParseMode, InlineQueryResultArticle, InputTextMessageContent
from db import db
from .buttons import poll_buttons
from .message import get_message_text
from wrappers import load_user


@load_user
def inline_search(bot, update, user):
    query = update.inline_query.query
    if not query:
        poll_list = db.get_user_polls(user)
    else:
        poll_list = db.search_poll(user, query)
    results = list()

    for poll in poll_list:
        message_text = get_message_text(poll, user)
        buttons = poll_buttons['answer'](poll)
        results.append(
            InlineQueryResultArticle(
                id=poll.id,
                title=poll.question,
                input_message_content=InputTextMessageContent(message_text=message_text,
                                                              parse_mode=ParseMode.HTML),
                reply_markup=buttons
            )
        )
    bot.answer_inline_query(update.inline_query.id, results)
