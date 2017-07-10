#!/usr/bin/python
# -*- coding: utf-8 -*-

#Inputs
import sqlite3

conn = sqlite3.connect('RSS.db')
c = conn.cursor()
#c.execute('SELECT * FROM stocks WHERE symbol=?', t)
sqlStatement = "SELECT * FROM RSS;"
c.execute(sqlStatement)
for row in c.execute(sqlStatement):
    print row

#conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
#conn.close()
