#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2, feedparser, time, sqlite3, telepot

bot = telepot.Bot('447936469:AAHzcTHK_R9D_U6qtyZzlyABIxvAFWPz6BA')

# Parameters:
conn = sqlite3.connect('RSS.db')
c = conn.cursor()
sqlStatement = "SELECT * FROM RSS"
for row in c.execute(sqlStatement):
    dbTitle = row[0]
    dbLink = row[1]
    dbRSSLink = row[2]
    dbDate = row[3]

    # Load RSS to string and parse it
    file = urllib2.urlopen(dbRSSLink)
    data = file.read()
    file.close()
    feed = feedparser.parse(dbRSSLink)

    for feed in feed["entries"]:
        # Create array with all titles from RSS feed
        title = feed["title"]
        for href in feed["links"]:
            # Create array with all topics' links from RSS feed
            href = href["href"]
        # Remove word Обновлено from title
        if (u'Обновлено' in title and dbTitle in title):
            title = title.split(" ", 1)[1]
        if dbLink.split('//')[1] in href:
            # Get part of title with series
            series = title.split(" / ")[3]
            seriesNew = series.split(" (")[0]
            # Get russian title from whole title string
            title = title.split(" / ")[0] + " | " + title.split(" / ")[2]

            # Date format 2016-12-16T12:29:42+00:00
            date = feed["updated"].split("+")[0]
            RSSdate = time.strptime(date, "%Y-%m-%dT%H:%M:%S")
            currentDate = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            currentDate = time.strptime(currentDate, "%Y-%m-%dT%H:%M:%S")
            if (RSSdate > time.strptime(dbDate, "%Y-%m-%dT%H:%M:%S")):
                message = 'Раздача обновлена\n'.decode('utf-8') + title + " | " + seriesNew + '\n' + dbLink
                bot.sendMessage(294967926, message)
                sqlStatement = 'UPDATE RSS SET date = ? WHERE linkToTopic = ?'
                values = (date, dbLink)
                c.execute(sqlStatement, values)
                conn.commit()

conn.close()
