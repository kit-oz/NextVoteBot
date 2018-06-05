# -*- coding: utf-8 -*-

from __future__ import absolute_import

from telegram import ParseMode

from config import MESSAGES
from db import db
from wrappers import load_user
from .buttons import poll_buttons
from .message import get_message_text


@load_user
def done(bot, update, user):
    """Callback function when "Done" button are pressed"""
    poll_draft = db.get_poll_draft(user)
    if not poll_draft:
        show_help(bot, update)
        return

    if poll_draft.choices.count() == 0:
        bot.send_message(chat_id=update.message.chat_id,
                         text=MESSAGES['ERROR_NO_CHOICES'])
        return

    db.open_poll(poll_draft)

    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['POLL_CREATED'])
    poll_control_view(bot, update, user, poll_draft)


def show_help(bot, update):
    """Callback function for the /help command"""
    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['HELP'])


@load_user
def start(bot, update, user):
    """Callback function for the /start command"""
    db.delete_draft_poll(user)

    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['START'])


@load_user
def polls(bot, update, user):
    """Callback function for the /pols command"""
    user_polls = user.opened_polls

    message_text = "You don't have any polls yet."
    if len(user_polls) > 0:
        message_text = "Your polls\n\n"
        poll_list = []
        for index, poll in enumerate(user_polls):
            result_text = 'Nobody voted.'
            if poll.result_count > 0:
                result_text = '{} person voted.'.format(poll.result_count)
            poll_text = '{index}. <b>{question}</b> {results}\n/view_{id}'.format(
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


def poll_control_view(bot, update, user, poll):
    """Function for build poll administrator"""
    if poll.author == user:
        action = 'control' if poll.is_open() else 'close'
        buttons = poll_buttons[action](poll)
        bot.send_message(chat_id=update.message.chat_id,
                         text=get_message_text(poll, user, 'control'),
                         parse_mode=ParseMode.HTML,
                         reply_markup=buttons)
    else:
        poll_vote_view(bot, update, user, poll)


def poll_vote_view(bot, update, user, poll):
    """Show poll with answer buttons"""
    if poll.is_open():
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
    """Callback for other commands"""
    query = update.message.text
    if '/view_' in query:
        poll_id = query.split('_')[1]
        poll = db.get_poll(poll_id)
        if poll and poll.author == user:
            poll_control_view(bot, update, user, poll)
            return
    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['ERROR_UNKNOWN_COMMAND'])


def non_text_received(bot, update):
    """Callback on receiving non text message (image, sticker, etc.)"""
    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['ERROR_NOT_TEXT'])
