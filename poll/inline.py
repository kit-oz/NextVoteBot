# -*- coding: utf-8 -*-

from telegram import ParseMode
from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent

from db import db
from wrappers import load_user

from .buttons import poll_buttons
from .message import get_message_text


def text_received(bot, update):
    """Save incoming text messages as poll template"""
    message_text = update.message.text
    user = db.get_user_by_id(update.message.from_user)
    if user.is_write_question():
        db.poll_templates[user.id] = {
            'question': message_text,
            'choices': []
        }
        db.set_user_state(user, user.WRITE_FIRST_ANSWER)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Creating a new poll: '<b>{}</b>'\n\nPlease send me the first answer option.".format(message_text),
            parse_mode=ParseMode.HTML
        )
    elif user.is_write_first_answer():
        db.poll_templates[user.id]['choices'].append(message_text)
        db.set_user_state(user, user.WRITE_OTHER_ANSWER)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Good. Now send me another answer option.")
    elif user.is_write_other_answer():
        db.poll_templates[user.id]['choices'].append(message_text)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Good. Feel free to add more answer options.\n\nWhen you've added enough, "
                              "simply send /done or press the button below to finish creating the poll.")
    else:
        db.set_user_state(user, user.WRITE_QUESTION)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Let's create a new poll. First, send me the question.")


@load_user
def poll_search(bot, update, user):
    """Inline search polls by ID or question text"""
    query = update.inline_query.query
    if not query:
        poll_list = db.get_user_polls(user)
    else:
        poll_list = db.search_poll(user=user, query_text=query)
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
