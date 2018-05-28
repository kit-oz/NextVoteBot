# -*- coding: utf-8 -*-

import os


class Config:
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

    DATABASE_URI = 'sqlite:///app.db'

    ADMIN_USERS = int(os.environ.get('ADMIN_USER', 0))

    RESULT_VISIBLE_MSG = ['never', 'after answer', 'always']
