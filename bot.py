# -*- coding: utf-8 -*-

import logging

from telegram.ext import Updater

from config import ADMIN_USER
from config import BOT_TOKEN
from config import HOST_NAME
from config import PORT
from poll_bot import init_handlers


def init_logging(dispatcher):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    def error(bot, update, error):
        error_msg = 'Update "{}" caused error "{}"'.format(update, error)
        logger.warning(error_msg)
        bot.send_message(chat_id=ADMIN_USER,
                         text=error_msg)

    dispatcher.add_error_handler(error)


def run_bot(use_webhook=False):
    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    init_logging(dispatcher)
    init_handlers(dispatcher)

    if use_webhook:
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=BOT_TOKEN)
        updater.bot.setWebhook("https://{}/{}".format(HOST_NAME, BOT_TOKEN))
    else:
        updater.start_polling()

    updater.idle()
