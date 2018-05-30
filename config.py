# -*- coding: utf-8 -*-

import os


ADMIN_USERS = int(os.environ.get('ADMIN_USER', 0))
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
HOST_NAME = os.environ.get('HOST_NAME', '')
PORT_NUMBER = int(os.environ.get('PORT_NUMBER', 443))


DATABASE_URI = 'sqlite:///app.db'
RESULT_VISIBLE_MSG = ['never', 'after answer', 'always']
