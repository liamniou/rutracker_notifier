#!/usr/bin/python
# -*- coding: utf-8 -*-

#Inputs
import sqlite3, time

#Parameters:
linkToRss = raw_input('Enter link to RSS feed: ')
linkToTopic = raw_input('Enter link to topic: ')
ruTitle = raw_input('Enter name of the topic: ')
currentDate = "1991-01-01T00:00:00"

conn = sqlite3.connect('RSS.db')
c = conn.cursor()

# Insert a row of data
values = (ruTitle.decode('utf-8'), linkToTopic, linkToRss, currentDate)
sqlStatement = 'INSERT INTO RSS VALUES (?,?,?,?)'
c.execute(sqlStatement, values)
conn.commit()
conn.close()