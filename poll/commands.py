# -*- coding: utf-8 -*-

from __future__ import absolute_import
from telegram import ParseMode

from config import BOT_NAME, WAIT_QUESTION
from db import db
from config import POLL_OPEN
from .buttons import poll_buttons
from .message import get_message_text
from wrappers import load_user


def show_help(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="This bot will help you create polls. Use /start to create a poll here, then publish it to groups or send it to individual friends.\n\nSend /polls to manage your existing polls.")


@load_user
def start(bot, update, user):
    db.set_user_state(user, WAIT_QUESTION)

    bot.send_message(chat_id=update.message.chat_id,
                     text="Let's create a new poll. First, send me the question.")


@load_user
def done(bot, update, user):
    db.set_user_state(user, WAIT_QUESTION)

    poll = db.create_poll(user)
    if poll:
        bot.send_message(chat_id=update.message.chat_id,
                         text="👍 Poll created. You can now publish it to a group or send it to your friends in a private message. To do this, tap the button below or start your message in any other chat with @{} and select one of your polls to send.".format(BOT_NAME))
        poll_control_view(bot, update, poll)


@load_user
def polls(bot, update, user):
    user_polls = db.get_user_polls(user, with_closed=True)

    message_text = "You don't have any polls yet."
    if user_polls:
        message_text = "Your polls\n\n"
        poll_list = []
        for index, poll in enumerate(user_polls):
            result_text = 'Nobody voted.'
            if poll.result_count > 0:
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


@load_user
def poll_control_view(bot, update, user, poll):
    if user.is_author(poll):
        action = 'control' if poll.state == POLL_OPEN else 'close'
        buttons = poll_buttons[action](poll)
        bot.send_message(chat_id=update.message.chat_id,
                         text=get_message_text(poll, user, 'control'),
                         parse_mode=ParseMode.HTML,
                         reply_markup=buttons)
    else:
        poll_vote_view(bot, update, user, poll)


@load_user
def poll_vote_view(bot, update, user, poll):
    if poll.state == POLL_OPEN:
        bot.send_message(chat_id=update.message.chat_id,
                         text=get_message_text(poll, user),
                         parse_mode=ParseMode.HTML,
                         reply_markup=poll_buttons['answer'](poll))
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text=get_message_text(poll, user),
                         parse_mode=ParseMode.HTML)


@load_user
def unknown_command(bot, update, user):
    query = update.message.text
    if '/view_' in query:
        poll_id = query.split('_')[1]
        poll = db.get_poll_by_id(poll_id)
        if user.is_author(poll):
            poll_control_view(bot, update, poll)
            return
    bot.send_message(chat_id=update.message.chat_id,
                     text="Sorry, I didn't understand that command.")


def non_text_received(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Sorry, I only support text and emoji for questions and answers.")
