import os
import re
import killall
import difflib
import telebot
import threading
import urllib.request
import logging as log
from pymongo import MongoClient
from flask import Flask, request
from selectolax.parser import HTMLParser


TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('URL')
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
client = MongoClient("mongodb://mongodb:27017")
db = client.rutracker_subscription


def log_and_send_message_decorator(fn):
    def wrapper(message):
        log.info("[FROM {}] [{}]".format(message.chat.id, message.text))
        reply = fn(message)
        log.info("[TO {}] [{}]".format(message.chat.id, reply))
        bot.send_message(message.chat.id, reply)
    return wrapper


def get_html_page_title(url):
    with urllib.request.urlopen(url) as url_object:
        raw_html = url_object.read()
    selector = "meta"
    for node in HTMLParser(raw_html).css(selector):
        if 'name' in node.attributes and node.attributes['name'] == 'description':
            content = node.attributes['content']
            break
    return content


def validate_url(string):
    return re.match("http[s]://(rutracker)(.*)(forum/viewtopic.php\?t=.*)", string)


@bot.message_handler(commands=['start'])
@log_and_send_message_decorator
def greet_new_user(message):
    welcome_msg = "\nWelcome to Rutracker_notifier bot!\nCommands available:\n" \
                  "/add - Add rutracker topic to your subscription list\n" \
                  "/list - Print list of your subscriptions\n" \
                  "/delete - Delete topic from your subscriptions"
    if message.chat.first_name is not None:
        if message.chat.last_name is not None:
            reply = "Hello, {} {} {}".format(message.chat.first_name, message.chat.last_name, welcome_msg)
        else:
            reply = "Hello, {} {}".format(message.chat.first_name, welcome_msg)
    else:
        reply = "Hello, {} {}".format(message.chat.title, welcome_msg)
    db.users.insert_one({'telegram_id': message.chat.id, 'subscriptions': []})
    return reply


@bot.message_handler(commands=['add'])
@log_and_send_message_decorator
def add_page_subscription(message):
    page_url = message.text.replace('/add ', '', 1)
    if validate_url(page_url):
        page_title = get_html_page_title(page_url)
        db.url_title.update(
            {'url': page_url},
            {'$set': {'title': page_title}},
            upsert=True
        )
        db.users.update(
            {'telegram_id': message.chat.id},
            {'$addToSet': {'subscriptions': page_url}},
            upsert=True
        )
        reply = "Page was successfully added into your subscription list"
    else:
        reply = "The URL you've entered doesn't look like Rutracker URL. Check it and try one more time, please"
    return reply


@bot.message_handler(commands=['delete'])
@log_and_send_message_decorator
def delete_topic(message):
    page_url = message.text.replace('/delete ', '', 1)
    update_result = db.users.update(
        {'telegram_id': message.chat.id},
        {'$pull': {'subscriptions': page_url}},
        upsert=True
    )
    if update_result['nModified'] == 1:
        return 'The topic was successfully removed'
    else:
        return 'Nothing to remove'


@bot.message_handler(commands=['list'])
@log_and_send_message_decorator
def list_topics(message):
    user_entry = db.users.find_one({'telegram_id': message.chat.id})
    reply = "Your subscriptions are:\n"
    for subscription in user_entry['subscriptions']:
        reply += "{0}\n".format(subscription)
    return reply


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='{}/{}'.format(URL, TOKEN))
    return "!", 200


def notify_users(page_url, diff):
    users_to_notify = db.users.find(
        {'subscriptions': {'$elemMatch': {'$eq': page_url}}}
    )
    if users_to_notify.count() > 0:
        for user in users_to_notify:
            message_to_send = 'Page {} was updated. Diff: {}'.format(page_url, diff)
            log.info("[TO {}] [{}]".format(user['telegram_id'], message_to_send))
            bot.send_message(user['telegram_id'], message_to_send)
    return 0


def check_subscription_updates():
    users = db.users.find({})
    all_subscriptions = []
    for user in users:
        all_subscriptions.extend(user['subscriptions'])
    subscriptions = list(set(all_subscriptions))
    for subscription in subscriptions:
        page = db.url_title.find_one({'url': subscription})
        remote_title = get_html_page_title(subscription)
        if remote_title != page['title']:
            diff = [li for li in difflib.ndiff(page['title'], remote_title) if li[0] != ' ']
            log.info('{} changed: {}'.format(page['url'], diff))
            notify_users(page['url'], diff)
            db.url_title.update(
                {'url': page['url']},
                {'$set': {'title': remote_title}},
                upsert=True
            )
        else:
            log.info('{} not changed since last check'.format(page['url']))
    loop_check()


def loop_check():
    threading.Timer(600, check_subscription_updates).start()


def main():
    print(URL)
    print(TOKEN)
    log.basicConfig(level=log.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
    log.info('Starting killall...')
    killall.install()
    log.info('Starting loop check...')
    loop_check()
    log.info('Starting Flask...')
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


if __name__ == '__main__':
    main()
