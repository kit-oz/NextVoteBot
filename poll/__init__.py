# -*- coding: utf-8 -*-

from __future__ import absolute_import
from telegram.ext import Filters
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler

from .inline import text_received
from .button_callback import button_callback
from .inline import poll_search
from .commands import show_help, start, done, polls, unknown_command, non_text_received


def init_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('help', show_help))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('done', done))
    dispatcher.add_handler(CommandHandler('polls', polls))

    dispatcher.add_handler(MessageHandler(Filters.text, text_received))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    dispatcher.add_handler(InlineQueryHandler(poll_search))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))
    dispatcher.add_handler(MessageHandler((~ Filters.text), non_text_received))
