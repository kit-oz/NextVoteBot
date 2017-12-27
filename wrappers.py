# -*- coding: utf-8 -*-

from functools import wraps
from config import LIST_OF_ADMINS
from db import db


def admin_only(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def load_user(func):
    @wraps(func)
    def wrapper(bot, update, *args, **kwargs):
        from_user = None
        if update.message:
            from_user = update.message.from_user
        elif update.callback_query:
            from_user = update.callback_query.from_user
        elif update.inline_query:
            from_user = update.inline_query.from_user
        if from_user:
            user = db.get_user_by_id(from_user)
            if user:
                return func(bot, update, user, *args, **kwargs)
    return wrapper
