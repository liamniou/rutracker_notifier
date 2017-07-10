import sqlite3

conn = sqlite3.connect('RSS.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE RSS
             (ruTitle text, linkToTopic text, linkToRss text, date text)''')

