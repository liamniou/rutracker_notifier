#!/usr/bin/python3
# -*- coding: utf-8 -*-
import telebot
import re
import time
import logging as log
import threading
import signal
import sys
from config import token, database_name
from rss_checker import RSSchecker
from sqliter import SQLighter

bot = telebot.TeleBot(token, threaded=False)
sub_timer = None


def log_and_send_message_decorator(fn):
    def wrapper(message):
        log.info("[FROM {}] [{}]".format(message.chat.id, message.text))
        reply = fn(message)
        log.info("[TO {}] [{}]".format(message.chat.id, reply))
        bot.send_message(message.chat.id, reply)
    return wrapper


@bot.message_handler(commands=['start', 'help'])
@log_and_send_message_decorator
def greet_new_user(message):
    welcome_msg = "\nWelcome to Rutracker_notifier bot!\nCommands available:\n" \
                  "/add - Add rutracker topic to your subscription list\n" \
                  "/list - Print list of your subscriptions\n" \
                  "/delete - Delete topic from your subscriptions\n" \
                  "/help - Print help message"
    if message.chat.first_name is not None:
        if message.chat.last_name is not None:
            reply = "Hello, {} {} {}".format(message.chat.first_name, message.chat.last_name, welcome_msg)
        else:
            reply = "Hello, {} {}".format(message.chat.first_name, welcome_msg)
    else:
        reply = "Hello, {} {}".format(message.chat.title, welcome_msg)
    return reply


@bot.message_handler(commands=['add'])
@log_and_send_message_decorator
def add_topic(message):
    topic_url = message.text.replace('/add ', '', 1)
    valid_topic_url = validate_url(topic_url).group()
    if valid_topic_url:
        db = SQLighter(database_name)
        subscription = db.check_subscription(message.chat.id, valid_topic_url)
        if not subscription:
            rss_checker = RSSchecker()
            author_profile_id = rss_checker.get_profile_id(valid_topic_url)
            if author_profile_id:
                db.add_topic(message.chat.id, valid_topic_url, author_profile_id)
                reply = "Topic {0} was successfully added into your subscription list".format(valid_topic_url)
            else:
                reply = "Can't get author profile id of {}. Try again please.".format(valid_topic_url)
        else:
            reply = "This topic already exists in your subscription list"
    else:
        reply = "The URL you've entered doesn't look like rutracker URL. Check it and try one more time, please"
    return reply


@bot.message_handler(commands=['list'])
@log_and_send_message_decorator
def list_topics(message):
    db = SQLighter(database_name)
    sql_data = db.select_all_where('subscriptions', 'chat_id', message.chat.id)
    if sql_data:
        rss_checker = RSSchecker()
        reply = "Your subscriptions are:\n"
        for rows in sql_data:
            reply += "{0} - {1}\n".format(rows[1], rss_checker.get_topic_title(rows[1]).replace(' :: RuTracker.org', ''))
    else:
        reply = "You don't have any subscriptions :("
    return reply


@bot.message_handler(commands=['delete'])
@log_and_send_message_decorator
def delete_topic(message):
    topic_url = message.text.replace('/delete ', '', 1)
    db = SQLighter(database_name)
    subscription = db.check_subscription(message.chat.id, topic_url)
    if not subscription:
        reply = "Topic {0} was not found in your subscription list".format(topic_url)
    else:
        db.delete_topic(message.chat.id, topic_url)
        reply = "The topic was successfully deleted from your subscription list"
    return reply


def validate_url(string):
    valid_url = re.match("http[s]://(rutracker)(.*)(forum/viewtopic.php\?t=.*)", string)
    return valid_url


def check_subscription_updates():
    rss_checker = RSSchecker()
    updated_topics = rss_checker.check_updates()
    if updated_topics:
        db = SQLighter(database_name)
        subscriptions_data = db.select_all('subscriptions')
        for topic in updated_topics:
            for subscriptions_row in subscriptions_data:
                if topic[0] in subscriptions_row:
                    reply = "{0} was updated on {1}".format(topic[0], topic[1])
                    log.info("[TO {}] [{}]".format(subscriptions_row[0], reply))
                    bot.send_message(subscriptions_row[0], reply)
                    db.update('topics', 'last_update', topic[1], 'url', topic[0])
    else:
        log.info('No updates...')
    loop_check()


def loop_check():
    sub_timer = threading.Timer(600, check_subscription_updates)
    sub_timer.start()


def signal_handler(signal_number, frame):
    print('Received signal ' + str(signal_number)
          + '. Trying to end tasks and exit...')
    bot.stop_polling()
    sys.exit(0)


def main():
    log.basicConfig(level=log.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
    log.info('Bot was started.')
    # Signal handler doesn't work due to endless loop of check_subscription_updates in try/except
    # signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            log.info('Starting loop check...')
            loop_check()
            log.info('Starting bot polling...')
            bot.polling()
        except Exception as err:
            signal.signal(signal.SIGINT, signal_handler)
            log.error("Bot polling error: {0}".format(err.args))
            bot.stop_polling()
            time.sleep(10)


if __name__ == '__main__':
    main()
