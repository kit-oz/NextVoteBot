# -*- coding: utf-8 -*-

from __future__ import absolute_import

from db.common import db
from db.manager import DatabaseManager
from wrappers import admin_only


@admin_only
def show_stat(bot, update):
    """Show bot usage statistic"""
    authors_count = DatabaseManager.get_authors_count()
    polls_created = DatabaseManager.get_created_polls_count()
    choices_count = DatabaseManager.get_choices_count()
    results_count = DatabaseManager.get_results_count()

    messages = [
        'Users with polls: {}'.format(authors_count),
        'Total polls created: {}'.format(polls_created),
        'Avg choices per poll: {:.1f}'.format(choices_count / polls_created if polls_created > 0 else 0),
        'Avg votes per poll: {:.1f}'.format(results_count / polls_created if polls_created > 0 else 0),
    ]
    bot.send_message(chat_id=update.message.chat_id,
                     text='\n'.join(messages))


@admin_only
def create_db(bot, update):
    db.create_all()
    bot.send_message(chat_id=update.message.chat_id,
                     text='Database successfully created')
