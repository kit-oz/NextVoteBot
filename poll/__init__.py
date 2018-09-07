# -*- coding: utf-8 -*-

from __future__ import absolute_import
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import InlineQueryHandler

from .admin_commands import create_db
from .admin_commands import show_stat
from .button_callback import button_callback
from .commands import done
from .commands import non_text_received
from .commands import polls
from .commands import show_help
from .commands import start
from .commands import unknown_command
from .inline import text_received
from .inline import inline_query


def init_handlers(dispatcher):
    # Public commands
    dispatcher.add_handler(CommandHandler('help', show_help))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('done', done))
    dispatcher.add_handler(CommandHandler('polls', polls))

    # Admin commands
    dispatcher.add_handler(CommandHandler('stat', show_stat))
    dispatcher.add_handler(CommandHandler('create_db', create_db))

    # Other
    dispatcher.add_handler(MessageHandler(Filters.text, text_received))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    dispatcher.add_handler(InlineQueryHandler(inline_query))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))
    dispatcher.add_handler(MessageHandler((~ Filters.text), non_text_received))
