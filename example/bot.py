#!env/bin/python
# -*- coding: utf-8 -*-

import logging
from pprint import pprint
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from db import Database

from config import BOT_AUTH_TOKEN


def user_loader(method):
    def wrapper(self, bot, update, *args, **kwargs):
        user_id = int(update.effective_user.id)
        user = self.db.get_user(user_id=user_id)
        if not user:
            user = self.db.add_user(update.effective_user)
        print(user.id)
        return method(self, bot, update, *args, **kwargs)
    return wrapper


class Bot:
    def __init__(self, token):
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        self.db = Database()

        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        echo_handler = MessageHandler(Filters.text, self.echo)
        self.dispatcher.add_handler(echo_handler)

        caps_handler = CommandHandler('caps', self.caps, pass_args=True)
        self.dispatcher.add_handler(caps_handler)

        unknown_handler = MessageHandler(Filters.command, self.unknown)
        self.dispatcher.add_handler(unknown_handler)

        return

    def run(self):
        self.updater.start_polling()
        return

    @user_loader
    def start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Hello, human!")
        return

    @user_loader
    def echo(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text='{}'.format(update.message.text))
        return

    @user_loader
    def caps(self, bot, update, args):
        text_caps = ' '.join(args).upper()
        bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)
        return

    @user_loader
    def unknown(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Sorry, I didn't understand that command.")


a = Bot(BOT_AUTH_TOKEN)
a.run()
