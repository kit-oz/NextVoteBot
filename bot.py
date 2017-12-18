# -*- coding: utf-8 -*-

import os
import sys
from threading import Thread

import logging
from telegram.ext import Updater, CommandHandler

from config import BOT_AUTH_TOKEN
from wrappers import restricted
from commands import init_commands


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater = Updater(token=BOT_AUTH_TOKEN)

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @restricted
    def restart(bot, update):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    updater.dispatcher.add_handler(CommandHandler('restart', restart))
    init_commands(updater.dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
