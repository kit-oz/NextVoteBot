# -*- coding: utf-8 -*-

from __future__ import absolute_import

import html
from telegram import ParseMode

from config import MESSAGES
from db.manager import DatabaseManager
from wrappers import load_user
from .buttons import get_admin_buttons
from .message import get_message_text


@load_user
def done(bot, update, user):
    """Callback function when "Done" button are pressed"""
    poll_draft = DatabaseManager.get_poll_draft(user)
    if not poll_draft:
        show_help(bot, update)
        return

    if len(poll_draft.choices) == 0:
        bot.send_message(chat_id=update.message.chat_id,
                         text=MESSAGES['ERROR_NO_CHOICES'],
                         parse_mode=ParseMode.HTML)
        return

    DatabaseManager.save_draft_poll(poll_draft)

    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['POLL_CREATED'],
                     parse_mode=ParseMode.HTML)
    poll_admin_view(bot, update, user, poll_draft)


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
            if poll.votes > 0:
                result_text = '{} person voted.'.format(poll.votes)
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


def poll_admin_view(bot, update, user, poll):
    """Function for build poll administrator"""
    message_text = get_message_text(poll, user, action='admin')
    message_buttons = get_admin_buttons(poll)

    bot.send_message(chat_id=update.message.chat_id,
                     text=message_text,
                     parse_mode=ParseMode.HTML,
                     reply_markup=message_buttons)


def show_help(bot, update):
    """Callback function for the /help command"""
    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['HELP'],
                     parse_mode=ParseMode.HTML)


@load_user
def start(bot, update, user):
    """Callback function for the /start command"""
    DatabaseManager.delete_draft_poll(user)

    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['START'],
                     parse_mode=ParseMode.HTML)


@load_user
def unknown_command(bot, update, user):
    """Callback for other commands"""
    query = html.escape(update.message.text)
    if '/view_' in query:
        poll_id = query.split('_')[1]
        poll = DatabaseManager.get_poll(poll_id)
        if poll and poll.author == user:
            poll_admin_view(bot, update, user, poll)
            return
    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['ERROR_UNKNOWN_COMMAND'],
                     parse_mode=ParseMode.HTML)


def non_text_received(bot, update):
    """Callback on receiving non text message (image, sticker, etc.)"""
    bot.send_message(chat_id=update.message.chat_id,
                     text=MESSAGES['ERROR_NOT_TEXT'],
                     parse_mode=ParseMode.HTML)
