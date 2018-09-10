# -*- coding: utf-8 -*-
import telebot
import re
from sqliter import SQLighter
from config import token, database_name

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['add'])
def add_topic(message):
    topic_url = message.text
    valid_topic_url = validate_url(topic_url)
    if valid_topic_url:
        valid_topic_url = valid_topic_url[0]
        db = SQLighter(database_name)
        db.add_topic(message.chat.id, valid_topic_url)
        bot.send_message(
            message.chat.id, "Topic {0} was successfully added into your subscription list".format(valid_topic_url)
        )
    else:
        bot.send_message(
            message.chat.id, "The URL you've entered is not valid. Check it and try one more time, please"
        )


@bot.message_handler(commands=['list'])
def list_topics(message):
    db = SQLighter(database_name)
    topics = db.list_topics(message.chat.id)
    full_message_text = "Your subscriptions are:\n"
    for row in topics:
        full_message_text += "{}\n".format("".join(row))
    bot.send_message(message.chat.id, full_message_text)

def validate_url(string):
    valid_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return valid_url


if __name__ == '__main__':
    bot.polling(none_stop=True)
