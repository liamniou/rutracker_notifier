# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def add_topic(self, chat_id, topic_url, op_profile_id):
        with self.connection:
            topics_entry = self.cursor.execute(
                "SELECT * FROM topics WHERE url = '{0}'".format(topic_url)
            ).fetchall()
            if not topics_entry:
                self.insert_into_table('topics', topic_url, "1991-01-01T00:00:00+00:00")
            self.insert_into_table('subscriptions', chat_id, topic_url, op_profile_id)
        return 0

    def insert_into_table(self, table_name, *arg):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO {0} VALUES {1}".format(table_name, arg)
            )

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

    def select_all(self, table_name):
        with self.connection:
            return self.cursor.execute("SELECT * FROM '{0}'".format(table_name)).fetchall()

    def select_all_where(self, table_name, column_name, value):
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM {0} WHERE {1} = '{2}'".format(table_name, column_name, value)
            ).fetchall()

    def update(self, table_name, column_name_to_update, new_value, column_name_for_where, value_for_where):
        with self.connection:
            return self.cursor.execute(
                "UPDATE {0} SET {1} = '{2}' WHERE {3} = '{4}'".format(
                    table_name, column_name_to_update, new_value, column_name_for_where, value_for_where
                )
            )

    def close(self):
        self.connection.close()
