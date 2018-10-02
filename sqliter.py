# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def add_topic(self, chat_id, topic_url):
        with self.connection:
            topics_entry = self.cursor.execute(
                "SELECT * FROM topics WHERE url = '{0}'".format(topic_url)
            ).fetchall()
            if not topics_entry:
                self.cursor.execute(
                    "INSERT INTO topics VALUES ('{0}', '{1}')".format(topic_url, "1991-01-01T00:00:00")
                )
            return self.cursor.execute(
                "INSERT INTO subscriptions VALUES ('{0}', '{1}')".format(chat_id, topic_url)
            )

    def list_topics(self, chat_id):
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM subscriptions WHERE chat_id = {0}".format(chat_id)
            ).fetchall()

    def check_subscription(self, chat_id, topic_url):
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM subscriptions WHERE chat_id = '{0}' and url = '{1}'".format(chat_id, topic_url)
            ).fetchall()

    def delete_topic(self, chat_id, topic_url):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM subscriptions WHERE chat_id = '{0}' and url = '{1}'".format(chat_id, topic_url)
            )

    def get_all_data_from_topics(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM topics").fetchall()

    def close(self):
        self.connection.close()
