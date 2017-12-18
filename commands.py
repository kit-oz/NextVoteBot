# -*- coding: utf-8 -*-

from telegram import ParseMode, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Filters
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler

from config import WAIT_QUESTION, WAIT_FIRST_CHOICE, WAIT_CHOICE
from model import Poll, Choice
from db import session, unsaved_polls
from db import get_user, set_user_state, create_poll
from message import button_callback


def show_help(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="This bot will help you create polls. Use /start to create a poll here, then publish it to groups or send it to individual friends.\n\nSend /polls to manage your existing polls.")


def start(bot, update):
    user = get_user(update.message.from_user.id)
    set_user_state(user, WAIT_QUESTION)

    bot.send_message(chat_id=update.message.chat_id,
                     text="Let's create a new poll. First, send me the question.")


def done(bot, update):
    user = get_user(update.message.from_user.id)
    set_user_state(user, WAIT_QUESTION)

    if user.id in unsaved_polls:
        poll = create_poll(author=user, raw_poll=unsaved_polls[user.id])
        if poll:
            bot.send_message(chat_id=update.message.chat_id,
                             text="👍 Poll created. You can now publish it to a group or send it to your friends in a private message. To do this, tap the button below or start your message in any other chat with @vote and select one of your polls to send.")


def polls(bot, update):
    user = get_user(update.message.from_user.id)
    poll_list = [poll.text for poll in session.query(Poll).filter(Poll.author_id == user.id).all()]
    text_answer = '\n'.join(poll_list)

    bot.send_message(chat_id=update.message.chat_id,
                     text="Your polls\n\n{}".format(text_answer))


def text_received(bot, update):
    message_text = update.message.text
    user = get_user(update.message.from_user.id)
    if user.state == WAIT_QUESTION:
        unsaved_polls[user.id] = {
            'question': message_text,
            'choices': []
        }
        set_user_state(user, WAIT_FIRST_CHOICE)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Creating a new poll: '*{}*'\n\nPlease send me the first answer option.".format(message_text),
            parse_mode=ParseMode.MARKDOWN
        )
    elif user.state == WAIT_FIRST_CHOICE:
        unsaved_polls[user.id]['choices'].append(message_text)
        set_user_state(user, WAIT_CHOICE)
        bot.send_message(chat_id=update.message.chat_id, text="Good. Now send me another answer option.")
    elif user.state == WAIT_CHOICE:
        unsaved_polls[user.id]['choices'].append(message_text)
        bot.send_message(chat_id=update.message.chat_id, text="Good. Feel free to add more answer options.\n\nWhen you've added enough, simply send /done or press the button below to finish creating the poll.")
    else:
        set_user_state(user, WAIT_QUESTION)
        bot.send_message(chat_id=update.message.chat_id, text="Let's create a new poll. First, send me the question.")


def inline_search(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    bot.answer_inline_query(update.inline_query.id, results)


def unknown_command(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def non_text_received(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Sorry, I only support text and emoji for questions and answers.")


def init_commands(dispatcher):
    dispatcher.add_handler(CommandHandler('help', show_help))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('done', done))
    dispatcher.add_handler(CommandHandler('polls', polls))

    dispatcher.add_handler(MessageHandler(Filters.text, text_received))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    dispatcher.add_handler(InlineQueryHandler(inline_search))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))
    dispatcher.add_handler(MessageHandler((~ Filters.text), non_text_received))
