# -*- coding: utf-8 -*-
import telebot
import re
import time
import threading
import signal
import sys
import cherrypy
from config import token, database_name
from config import WEBHOOK_HOST, WEBHOOK_PORT, WEBHOOK_LISTEN, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV
from rss_checker import RSSchecker
from sqliter import SQLighter

bot = telebot.TeleBot(token)
sub_timer = None

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (token)


# WebhookServer, process webhook calls
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length)
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_messages([update.message])
            return ''
        else:
            raise cherrypy.HTTPError(403)

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
            rss_checker = RSSchecker()
            op_profile_id = rss_checker.get_profile_id(valid_topic_url)
            db.add_topic(message.chat.id, valid_topic_url, op_profile_id)
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
    sql_data = db.select_all_where('subscriptions', 'chat_id', message.chat.id)
    full_message_text = "Your subscriptions are:\n"
    if sql_data:
        rss_checker = RSSchecker()
        for rows in sql_data:
            full_message_text += "{0} - {1}\n".format(rows[1], rss_checker.get_topic_title(rows[1]).replace(' :: RuTracker.org', ''))
        bot.send_message(message.chat.id, full_message_text)
    else:
        bot.send_message(message.chat.id, 'You don''t have any subscriptions :(')


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


def check_subscription_updates():
    rss_checker = RSSchecker()
    updated_topics = rss_checker.check_updates()
    if updated_topics:
        db = SQLighter(database_name)
        subscriptions_data = db.select_all('subscriptions')
        for topic in updated_topics:
            for subscriptions_row in subscriptions_data:
                if topic[0] in subscriptions_row:
                    bot.send_message(
                        subscriptions_row[0], "{0} was updated on {1}".format(topic[0], topic[1])
                    )
                    db.update('topics', 'last_update', topic[1], 'url', topic[0])
                    time.sleep(2)
    else:
        print('No updates')
    loop_check()


def loop_check():
    sub_timer = threading.Timer(120, check_subscription_updates)
    sub_timer.start()


def signal_handler(signal_number, frame):
    print('Received signal ' + str(signal_number)
          + '. Trying to end tasks and exit...')
    bot.stop_polling()
    sub_timer.cancel()
    sys.exit(0)


def main():
    loop_check()

    signal.signal(signal.SIGINT, signal_handler)

    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()

    # Set webhook
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    # Start cherrypy server
    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
    })

    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})


if __name__ == '__main__':
    main()
