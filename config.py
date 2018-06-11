# -*- coding: utf-8 -*-

import os


ADMIN_USER = int(os.environ.get("ADMIN_USER", 0))
BOT_TOKEN = os.environ.get("BOT_TOKEN", '')
HOST_NAME = os.environ.get("HOST_NAME", '')
PORT = int(os.environ.get("PORT", 443))


DATABASE_URI = "sqlite:///app.db"
RESULT_VISIBLE_MSG = ["never", "after answer", "always"]

MESSAGES = {
    "ERROR_NO_CHOICES": "Sorry, a poll needs to have a question and at least one answer option to work.\n"
                        "Please send me the first answer option.",
    "ERROR_NOT_TEXT": "Sorry, I only support text and emoji for questions and answers.",
    "ERROR_UNKNOWN_COMMAND": "Sorry, I didn't understand that command.",
    "HELP": "This bot will help you create polls. Use /start to create a poll here, "
            "then publish it to groups or send it to individual friends.\n\n"
            "Send /polls to manage your existing polls.",
    "POLL_CREATED": "👍 Poll created. You can now publish it to a group or send it to your friends "
                    "in a private message. To do this, tap the button below or start your message "
                    "in any other chat with @NextVoteBot and select one of your polls to send.",
    "POLL_DELETE_ALERT": "\n<b>Deleting a poll with permanently remove it from your inline suggestions "
                         "and bot settings. It will appear closed to all other users.\n\nDelete poll?</b>",
    "POLL_FOOTER_CLOSED": "<i>Poll closed.</i>",
    "POLL_FOOTER_NO_VOTES": "👥Nobody voted so far.",
    "POLL_FOOTER_ONE_VOTE": "1 person voted so far.",
    "POLL_FOOTER_VOTES": "{votes} people voted so far.",
    "START": "Let's create a new poll. First, send me the question.",
}
