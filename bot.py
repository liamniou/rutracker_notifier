# -*- coding: utf-8 -*-
import config
import telebot
import time, os

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['test'])
def send_message(message):
    bot.send_message(message.chat.id, "Some feedback")


@bot.message_handler(content_types=["text"])
def capture_message(message):
    print(message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
