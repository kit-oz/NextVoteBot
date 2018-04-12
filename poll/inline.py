# -*- coding: utf-8 -*-

from telegram import ParseMode

from db import db


def text_received(bot, update):
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
                         text="Good. Feel free to add more answer options.\n\nWhen you've added enough, simply send /done or press the button below to finish creating the poll.")
    else:
        db.set_user_state(user, user.WRITE_QUESTION)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Let's create a new poll. First, send me the question.")
