# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def add_topic(self, chat_id, topic_url):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO subscriptions VALUES ('{0}', '{1}')".format(chat_id, topic_url)
            )

    def list_topics(self, chat_id):
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM subscriptions WHERE chat_id = {0}".format(chat_id)
            ).fetchall()

    def close(self):
        self.connection.close()
