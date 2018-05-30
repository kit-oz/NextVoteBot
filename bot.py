# -*- coding: utf-8 -*-

import logging

from telegram.ext import Updater

from config import BOT_TOKEN, HOST_NAME, PORT_NUMBER
from poll import init_handlers


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    def error(bot, update, error):
        logger.warning('Update "%s" caused error "%s"', update, error)

    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher
    init_handlers(dp)
    dp.add_error_handler(error)

    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT_NUMBER,
                          url_path=BOT_TOKEN)
    updater.bot.setWebhook("https://{}:{}/{}".format(HOST_NAME, PORT_NUMBER, BOT_TOKEN))
    updater.idle()


if __name__ == '__main__':
    main()
