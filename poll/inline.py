# -*- coding: utf-8 -*-

from telegram import ParseMode
from db import db
from config import WAIT_QUESTION, WAIT_FIRST_CHOICE, WAIT_CHOICE


def text_received(bot, update):
    message_text = update.message.text
    user = db.get_user_by_id(update.message.from_user)
    if user.state == WAIT_QUESTION:
        db.poll_templates[user.id] = {
            'question': message_text,
            'choices': []
        }
        db.set_user_state(user, WAIT_FIRST_CHOICE)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Creating a new poll: '<b>{}</b>'\n\nPlease send me the first answer option.".format(message_text),
            parse_mode=ParseMode.HTML
        )
    elif user.state == WAIT_FIRST_CHOICE:
        db.poll_templates[user.id]['choices'].append(message_text)
        db.set_user_state(user, WAIT_CHOICE)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Good. Now send me another answer option.")
    elif user.state == WAIT_CHOICE:
        db.poll_templates[user.id]['choices'].append(message_text)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Good. Feel free to add more answer options.\n\nWhen you've added enough, simply send /done or press the button below to finish creating the poll.")
    else:
        db.set_user_state(user, WAIT_QUESTION)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Let's create a new poll. First, send me the question.")
