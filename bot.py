# -*- coding: utf-8 -*-

import logging

from telegram.ext import Updater

from config import BOT_TOKEN
from config import HOST_NAME
from config import PORT
from poll import init_handlers


def init_logging(dispatcher):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    def error(bot, update, error):
        logger.warning('Update "%s" caused error "%s"', update, error)
    pass

    dispatcher.add_error_handler(error)


def main():
    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    init_logging(dispatcher)
    init_handlers(dispatcher)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=BOT_TOKEN)
    updater.bot.setWebhook("https://{}/{}".format(HOST_NAME, BOT_TOKEN))
    updater.idle()


if __name__ == '__main__':
    main()
