# -*- coding: utf-8 -*-

from functools import wraps

from config import ADMIN_USER
from config import MESSAGES
from db.manager import DatabaseManager


def admin_only(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != ADMIN_USER:
            bot.send_message(chat_id=update.message.chat_id, text=MESSAGES['ERROR_UNKNOWN_COMMAND'])
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def load_user(func):
    @wraps(func)
    def wrapper(bot, update, *args, **kwargs):
        from_user = update.effective_user
        if from_user:
            if from_user.is_bot:
                return

            user = DatabaseManager.get_user(from_user)
            if user:
                return func(bot, update, user, *args, **kwargs)
    return wrapper
