# -*- coding: utf-8 -*-

import json

config = json.load(open('config.json'))


class Config:
    BOT_TOKEN = config['bot']['token']

    DATABASE_URI = config['database']['uri']

    ADMIN_USERS = config['admin_users']

    RESULT_VISIBLE_MSG = ['never', 'after answer', 'always']
