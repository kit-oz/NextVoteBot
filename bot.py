# -*- coding: utf-8 -*-

import logging
import os
import sys
from threading import Thread

from telegram.ext import Updater
from telegram.ext import CommandHandler

from config import BOT_TOKEN, HOST_NAME, PORT_NUMBER
from poll import init_handlers
from wrappers import admin_only


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater = Updater(token=BOT_TOKEN)

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    @admin_only
    def restart(bot, update):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    updater.dispatcher.add_handler(CommandHandler('restart', restart))
    init_handlers(updater.dispatcher)

    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT_NUMBER,
                          url_path=BOT_TOKEN)
    updater.bot.setWebhook("https://{}:{}/{}".format(HOST_NAME, PORT_NUMBER, BOT_TOKEN))
    updater.idle()


if __name__ == '__main__':
    main()
