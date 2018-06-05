# -*- coding: utf-8 -*-

from telegram import ParseMode
from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent

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
def poll_search(bot, update, user):
    """Inline search polls by ID or question text"""
    query = update.inline_query.query
    poll_list = DatabaseManager.get_user_polls(user=user, query_text=query)

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
