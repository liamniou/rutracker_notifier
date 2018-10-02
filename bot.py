# -*- coding: utf-8 -*-
import telebot
import re
import schedule
import time
from multiprocessing import Process
from sqliter import SQLighter
from config import token, database_name

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def greet_new_user(message):
    welcome_msg = "\nWelcome to Rutracker_notifier bot!\nCommands available:\n" \
                  "/add - Add rutracker topic to your subscription list\n" \
                  "/list - Print list of your subscriptions\n" \
                  "/delete - Delete topic from your subscriptions\n" \
                  "/help - Print help message"
    if message.chat.first_name is not None:
        if message.chat.last_name is not None:
            bot.send_message(
                message.chat.id, "Hello, " + message.chat.first_name + " " + message.chat.last_name + welcome_msg
            )
        else:
            bot.send_message(message.chat.id, "Hello, " + message.chat.first_name + welcome_msg)
    else:
        bot.send_message(message.chat.id, "Hello, " + message.chat.title + welcome_msg)


@bot.message_handler(commands=['add'])
def add_topic(message):
    topic_url = message.text.replace('/add ', '', 1)
    valid_topic_url = validate_url(topic_url).group()
    if valid_topic_url:
        db = SQLighter(database_name)
        subscription = db.check_subscription(message.chat.id, valid_topic_url)
        if not subscription:
            db.add_topic(message.chat.id, valid_topic_url)
            bot.send_message(
                message.chat.id, "Topic {0} was successfully added into your subscription list".format(valid_topic_url)
            )
        else:
            bot.send_message(
                message.chat.id, "This topic already exists in your subscription list".format(valid_topic_url)
            )
    else:
        bot.send_message(
            message.chat.id,
            "The URL you've entered doesn't look like rutracker URL. Check it and try one more time, please"
        )


@bot.message_handler(commands=['list'])
def list_topics(message):
    db = SQLighter(database_name)
    sql_data = db.list_topics(message.chat.id)
    full_message_text = "Your subscriptions are:\n"
    for rows in sql_data:
        full_message_text += "{}\n".format(rows[1])
    bot.send_message(message.chat.id, full_message_text)


@bot.message_handler(commands=['delete'])
def delete_topic(message):
    topic_url = message.text.replace('/delete ', '', 1)
    db = SQLighter(database_name)
    subscription = db.check_subscription(message.chat.id, topic_url)
    if not subscription:
        bot.send_message(
            message.chat.id, "Topic {0} was not found in your subscription list".format(topic_url)
        )
    else:
        db.delete_topic(message.chat.id, topic_url)
        bot.send_message(
            message.chat.id, "The topic was successfully deleted from your subscription list".format(topic_url)
        )


def validate_url(string):
    valid_url = re.match("http[s]://(rutracker)(.*)(forum/viewtopic.php\?t=.*)", string)
    return valid_url


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


def scheduled_check():
    while True:
        bot.send_message(
            294967926, "Hello"
        )
        time.sleep(60)


if __name__ == '__main__':
    p1 = Process(target=scheduled_check, args=())
    p1.start()
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(e)
            time.sleep(15)
            #telegram_polling()
