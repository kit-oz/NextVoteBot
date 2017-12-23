# -*- coding: utf-8 -*-

from __future__ import absolute_import
from telegram import ParseMode

from config import BOT_NAME, WAIT_QUESTION
from db.middleware import db
from .buttons import poll_buttons
from .message import get_message_text


def show_help(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="This bot will help you create polls. Use /start to create a poll here, then publish it to groups or send it to individual friends.\n\nSend /polls to manage your existing polls.")


def start(bot, update):
    user = db.get_user_by_id(update.message.from_user.id)
    db.set_user_state(user, WAIT_QUESTION)

    bot.send_message(chat_id=update.message.chat_id,
                     text="Let's create a new poll. First, send me the question.")


def done(bot, update):
    user = db.get_user_by_id(update.message.from_user.id)
    db.set_user_state(user, WAIT_QUESTION)

    poll = db.create_poll(user)
    if poll:
        bot.send_message(chat_id=update.message.chat_id,
                         text="👍 Poll created. You can now publish it to a group or send it to your friends in a private message. To do this, tap the button below or start your message in any other chat with @{} and select one of your polls to send.".format(BOT_NAME))
        poll_control_view(bot, update, poll)


def polls(bot, update):
    user = db.get_user_by_id(update.message.from_user.id)
    user_polls = db.get_user_polls(user)

    message_text = "You don't have any polls yet."
    if user_polls:
        message_text = "Your polls\n\n"
        poll_list = []
        for index, poll in enumerate(user_polls):
            result_text = 'Nobody voted.'
            if poll.result_count == 0:
                result_text = '{} person voted.'.format(poll.result_count)
            poll_text = '{index}. {question} <code>{results}</code>\n/view_{id}'.format(
                index=index + 1,
                question=poll.question,
                results=result_text,
                id=poll.id
            )
            poll_list.append(poll_text)
        message_text += '\n'.join(poll_list)

    bot.send_message(chat_id=update.message.chat_id,
                     text=message_text,
                     parse_mode=ParseMode.HTML)


def poll_control_view(bot, update, poll):
    user = db.get_user_by_id(update.message.from_user.id)

    if user.id == poll.user_id:
        bot.send_message(chat_id=update.message.chat_id,
                         text=get_message_text(poll, user, 'control'),
                         parse_mode=ParseMode.HTML,
                         reply_markup=poll_buttons['control'](poll))


def poll_vote_view(bot, update, poll):
    user = db.get_user_by_id(update.message.from_user.id)
    print(update)

    if user.id == poll.user_id:
        bot.send_message(chat_id=update.message.chat_id,
                         text=get_message_text(poll, user),
                         parse_mode=ParseMode.HTML,
                         reply_markup=poll_buttons['answer'](poll))


def unknown_command(bot, update):
    query = update.message.text
    if '/view_' in query:
        poll_id = query.split('_')[1]
        poll = db.get_poll_by_id(poll_id)
        poll_control_view(bot, update, poll)
        return
    bot.send_message(chat_id=update.message.chat_id,
                     text="Sorry, I didn't understand that command.")


def non_text_received(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Sorry, I only support text and emoji for questions and answers.")
