# -*- coding: utf-8 -*-

# Next Vote Bot
BOT_AUTH_TOKEN = '471075290:AAGv-38b1tRzTE7J3VLfkluOskbqu0tG5h4'
BOT_NAME = 'NextVoteBot'

SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

LIST_OF_ADMINS = [131031814]

POLL_CODE_LENGTH = 7
INLINE_SEARCH_RESULTS = 5

# Current chat states
WAIT_QUESTION = 0
WAIT_FIRST_CHOICE = 1
WAIT_CHOICE = 2

# Poll states
POLL_OPEN = 0
POLL_CLOSED = 1
POLL_DELETED = 2

# Results visibility options
VISIBLE_NEVER = 0
VISIBLE_AFTER_ANSWER = 1
VISIBLE_ALWAYS = 2
VISIBLE_TEXT = ['never', 'after answer', 'always']
